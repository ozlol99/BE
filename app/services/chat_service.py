import time
from typing import Any, List, cast

from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.functions import Count

from app.dtos.chat_dto import (
    ChatRoomCardResponse,
    ChatRoomCreate,
    ChatRoomDetailResponse,
    ChatRoomUpdate,
    HashtagResponse,
    JoinRoomRequest,
    ParticipantResponse,
    ParticipantRiotAccountResponse,
)
from app.models.chat_room import ChatRoom
from app.models.chat_room_participant import ChatRoomParticipant
from app.models.hash_tag import HashTag
from app.models.riot_account import RiotAccount
from app.models.user import UserModel
from app.services import chat_riot_service, summoner_search_service


# Helper function for time
def _format_time_ago(dt):
    if dt is None:
        return "N/A"
    now = time.time()
    created_at_ts = dt.timestamp()
    diff = int(now - created_at_ts)

    if diff < 60:
        return f"{diff}초 전"
    elif diff < 3600:
        return f"{diff // 60}분 전"
    elif diff < 86400:
        return f"{diff // 3600}시간 전"
    else:
        return f"{diff // 86400}일 전"


async def create_chat_room(room_data: ChatRoomCreate, owner: UserModel) -> ChatRoom:
    try:
        chat_room = await ChatRoom.create(
            name=room_data.name,
            owner=owner,
            max_members=room_data.max_members,
            queue_type=room_data.queue_type,
        )
    except IntegrityError as e:
        if "Duplicate entry" in str(e) and "queue_type" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Chat room with queue type '{room_data.queue_type}' already exists.",
            )
        raise  # Re-raise other IntegrityErrors

    if room_data.hashtags:
        for tag_name in room_data.hashtags:
            hashtag, _ = await HashTag.get_or_create(name=tag_name)
            await chat_room.hashtags.add(hashtag)

    return chat_room


async def get_chat_room_list() -> List[ChatRoomCardResponse]:
    rooms = (
        await ChatRoom.all()
        .prefetch_related("owner", "hashtags")
        .annotate(current_members=Count("participants"))
    )

    response = []
    for room in rooms:
        # Cast room to Any to bypass Mypy's check for dynamically added attributes
        room_with_members = cast(Any, room)
        response.append(
            ChatRoomCardResponse(
                id=room_with_members.id,
                name=room_with_members.name,
                current_members=room_with_members.current_members,
                max_members=room_with_members.max_members,
                queue_type=room_with_members.queue_type.value,
                hashtags=[
                    HashtagResponse(id=tag.id, name=tag.name)
                    for tag in room_with_members.hashtags
                ],
                owner_nickname=room_with_members.owner.user,
                created_ago=_format_time_ago(room_with_members.created_at),
            )
        )
    return response


async def get_chat_room_details(room_id: int) -> ChatRoomDetailResponse:
    try:
        room = await ChatRoom.get(id=room_id).prefetch_related("owner", "hashtags")
        participants = await ChatRoomParticipant.filter(
            room_id=room_id
        ).prefetch_related("user", "riot_account")

        participant_responses = []
        for p in participants:
            summoner_info = await summoner_search_service.get_summoner_info(
                p.riot_account.game_name, p.riot_account.tag_line
            )
            rank_info = await chat_riot_service.get_summoner_rank_info(
                summoner_info["puuid"]
            )
            tier = rank_info.get("solo_rank", {}).get("tier", "UNRANKED")
            tier_icon = chat_riot_service.get_tier_icon_url(tier)

            participant_responses.append(
                ParticipantResponse(
                    user_id=p.user.id,
                    nickname=p.user.user,
                    position=p.position.value,
                    riot_account=ParticipantRiotAccountResponse(
                        game_name=p.riot_account.game_name,
                        tag_line=p.riot_account.tag_line,
                    ),
                    tier_icon_url=tier_icon,
                )
            )

        return ChatRoomDetailResponse(
            id=room.id,
            name=room.name,
            owner_id=room.owner.id,
            max_members=room.max_members,
            current_members=len(participants),
            queue_type=room.queue_type.value,
            hashtags=[
                HashtagResponse(id=tag.id, name=tag.name) for tag in room.hashtags
            ],
            participants=participant_responses,
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found"
        )


async def update_chat_room(
    room_id: int, room_data: ChatRoomUpdate, user: UserModel
) -> ChatRoom:
    try:
        room = await ChatRoom.get(id=room_id, owner=user)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not the owner or room does not exist",
        )

    if room_data.name:
        room.name = room_data.name

    if room_data.hashtags is not None:
        await room.hashtags.clear()
        for tag_name in room_data.hashtags:
            hashtag, _ = await HashTag.get_or_create(name=tag_name)
            await room.hashtags.add(hashtag)

    await room.save()
    return room


async def delete_chat_room(room_id: int, user: UserModel):
    try:
        room = await ChatRoom.get(id=room_id, owner=user)
        await room.delete()
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not the owner or room does not exist",
        )


async def join_chat_room(room_id: int, join_data: JoinRoomRequest, user: UserModel):
    try:
        riot_account = await RiotAccount.get(id=join_data.riot_account_id, user=user)
        room = await ChatRoom.get(id=room_id)

        current_participants = await ChatRoomParticipant.filter(room_id=room_id).count()
        if current_participants >= room.max_members:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Room is full"
            )

        await ChatRoomParticipant.create(
            user=user, room=room, riot_account=riot_account, position=join_data.position
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid room, account, or position.",
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Position already taken or user already in room.",
        )


async def leave_chat_room(room_id: int, user: UserModel):
    try:
        room = await ChatRoom.get(id=room_id).prefetch_related("owner")
        if room.owner.id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner cannot leave the room, must delete it instead.",
            )

        participant = await ChatRoomParticipant.get(room_id=room_id, user=user)
        await participant.delete()
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="You are not in this room."
        )
