import time
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)

# DTO Import
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

router = APIRouter(prefix="/chat", tags=["Chat"])

# CRUD Endpoints


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


@router.post("/rooms/{room_id}/join", status_code=status.HTTP_201_CREATED)
async def join_room(
    room_id: int,
    join_data: JoinRoomRequest,
    current_user: UserModel = Depends(get_current_user),
):
    await chat_service.join_chat_room(room_id, join_data, current_user)
    return {"detail": "Successfully joined the room."}


@router.post("/rooms/{room_id}/leave", status_code=status.HTTP_200_OK)
async def leave_room(room_id: int, current_user: UserModel = Depends(get_current_user)):
    await chat_service.leave_chat_room(room_id, current_user)
    return {"detail": "Successfully left the room."}


# WebSocket Endpoint


async def get_participant_from_token(
    token: str, room_id: int
) -> Optional[ChatRoomParticipant]:
    try:
        payload = verify_access_token(token)
        if not payload or "sub" not in payload:
            return None

        user = await UserModel.get_or_none(email=payload["sub"])
        if not user:
            return None

        participant = await ChatRoomParticipant.get(
            room_id=room_id, user=user
        ).prefetch_related("riot_account", "user")
        return participant
    except Exception:
        return None


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    auth_header = websocket.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    participant = await get_participant_from_token(token, room_id)
    if not participant:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, str(room_id))

    join_message = {
        "type": "user_join",
        "user_id": participant.user.id,
        "username": participant.riot_account.game_name,
        "timestamp": time.time(),
    }
    await manager.broadcast(join_message, str(room_id))

    try:
        while True:
            data = await websocket.receive_text()
            message = {
                "type": "chat_message",
                "sender_id": participant.user.id,
                "username": participant.riot_account.game_name,
                "content": data,
                "timestamp": time.time(),
            }
            await manager.broadcast(message, str(room_id))
    except WebSocketDisconnect:
        manager.disconnect(websocket, str(room_id))
        leave_message = {
            "type": "user_leave",
            "user_id": participant.user.id,
            "username": participant.riot_account.game_name,
            "timestamp": time.time(),
        }
        await manager.broadcast(leave_message, str(room_id))
