import logging
import time
import traceback
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from app.dtos.chat_dto import (
    ChatRoomCardResponse,
    ChatRoomCreate,
    ChatRoomDetailResponse,
    ChatRoomUpdate,
    JoinRoomRequest,
)
from app.models.chat_room_participant import ChatRoomParticipant

# Model Imports
from app.models.user import UserModel

# Service Imports
from app.services import chat_service
from app.services.connection_manager import manager
from app.services.token_service import get_current_user, verify_access_token

log = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/rooms", status_code=status.HTTP_201_CREATED, response_model=ChatRoomDetailResponse
)
async def create_room(
    room_data: ChatRoomCreate, current_user: UserModel = Depends(get_current_user)
):
    new_room = await chat_service.create_chat_room(room_data, current_user)
    return await chat_service.get_chat_room_details(new_room.id)


@router.get("/rooms", response_model=List[ChatRoomCardResponse])
async def list_rooms():
    return await chat_service.get_chat_room_list()


@router.get("/rooms/{room_id}", response_model=ChatRoomDetailResponse)
async def get_room(room_id: int):
    return await chat_service.get_chat_room_details(room_id)


@router.put("/rooms/{room_id}", response_model=ChatRoomDetailResponse)
async def update_room(
    room_id: int,
    room_data: ChatRoomUpdate,
    current_user: UserModel = Depends(get_current_user),
):
    await chat_service.update_chat_room(room_id, room_data, current_user)
    return await chat_service.get_chat_room_details(room_id)


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int, current_user: UserModel = Depends(get_current_user)
):
    await chat_service.delete_chat_room(room_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/rooms/{room_id}/join",
    status_code=status.HTTP_201_CREATED,
    response_model=ChatRoomDetailResponse,
)
async def join_room(
    room_id: int,
    join_data: JoinRoomRequest,
    current_user: UserModel = Depends(get_current_user),
):
    await chat_service.join_chat_room(room_id, join_data, current_user)
    return await chat_service.get_chat_room_details(room_id)


@router.post("/rooms/{room_id}/leave", status_code=status.HTTP_200_OK)
async def leave_room(room_id: int, current_user: UserModel = Depends(get_current_user)):
    await chat_service.leave_chat_room(room_id, current_user)
    return {"detail": "Successfully left the room."}


@router.delete(
    "/rooms/{room_id}/participants/{participant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def kick_participant_from_room(
    room_id: int,
    participant_id: int,
    current_user: UserModel = Depends(get_current_user),
):
    await chat_service.kick_participant(room_id, participant_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# WebSocket Endpoint


async def get_participant_from_token(
    token: str, room_id: int
) -> Optional[ChatRoomParticipant]:
    log.info(f"[DEBUG] get_participant_from_token called for room {room_id}")
    try:
        payload = verify_access_token(token)
        if not payload or "sub" not in payload:
            log.warning("[DEBUG] Invalid payload or missing 'sub'")
            return None
        log.info(f"[DEBUG] Payload 'sub': {payload['sub']}")

        user = await UserModel.get_or_none(email=payload["sub"])
        if not user:
            log.warning(f"[DEBUG] User not found for email: {payload['sub']}")
            return None
        log.info(f"[DEBUG] User found: {user.id}")

        participant = await ChatRoomParticipant.get(
            room_id=room_id, user=user
        ).prefetch_related("riot_account", "user")
        log.info(f"[DEBUG] Participant found for user {user.id} in room {room_id}")
        return participant
    except Exception as e:
        log.error(f"[DEBUG] An exception occurred in get_participant_from_token: {e}")
        log.error(traceback.format_exc())
        return None


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, room_id: int, token: Optional[str] = None
):
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    participant = await get_participant_from_token(token, room_id)
    if not participant:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = participant.user.id
    await manager.connect(websocket, str(room_id), user_id)

    join_message = {
        "type": "user_join",
        "user_id": user_id,
        "username": participant.riot_account.game_name,
        "timestamp": time.time(),
    }
    await manager.broadcast(join_message, str(room_id))

    try:
        while True:
            data = await websocket.receive_text()
            message = {
                "type": "chat_message",
                "sender_id": user_id,
                "username": participant.riot_account.game_name,
                "content": data,
                "timestamp": time.time(),
            }
            await manager.broadcast(message, str(room_id))
    except WebSocketDisconnect:
        manager.disconnect(str(room_id), user_id)
        leave_message = {
            "type": "user_leave",
            "user_id": user_id,
            "username": participant.riot_account.game_name,
            "timestamp": time.time(),
        }
        await manager.broadcast(leave_message, str(room_id))
