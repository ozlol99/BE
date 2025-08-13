from fastapi import (
    APIRouter,
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from tortoise.exceptions import DoesNotExist

from app.models.chat_room import ChatRoom
from app.models.user import UserModel
from app.services.connection_manager import manager
from app.services.token_service import get_current_user, verify_access_token

router = APIRouter(prefix="/chat", tags=["chat"])


async def get_current_user_from_token(token: str = Query(...)) -> UserModel:
    if not token:
        raise WebSocketDisconnect(code=4001, reason="Token not provided")

    payload = verify_access_token(token)
    if payload is None:
        raise WebSocketDisconnect(code=4001, reason="Invalid or expired token")

    user_email: str | None = payload.get("sub")
    if user_email is None:
        raise WebSocketDisconnect(code=4001, reason="User info not in token")

    user = await UserModel.get_or_none(email=user_email)
    if user is None:
        raise WebSocketDisconnect(code=4001, reason="User not found")
    return user


@router.get("/rooms", description="전체 채팅방 목록 조회")
async def list_chat_rooms():
    rooms = (
        await ChatRoom.all()
        .prefetch_related("owner")
        .values("id", "name", "owner__user")
    )
    return [
        {"id": room["id"], "name": room["name"], "owner": room["owner__user"]}
        for room in rooms
    ]


@router.post("/rooms", description="채팅방 생성")
async def create_chat_room(
    name: str, current_user: UserModel = Depends(get_current_user)
):
    chat_room = await ChatRoom.create(name=name, owner=current_user)
    return {"room_id": chat_room.id, "name": chat_room.name}


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, room_id: str, token: str = Query(...)
):

    user = await get_current_user_from_token(token)
    if not user:
        return

    try:
        await ChatRoom.get(id=int(room_id))
    except DoesNotExist:
        await websocket.close(code=4004, reason="Room not found")
        return

    if manager.get_active_user_count(room_id) >= 5:
        await websocket.close(code=4000, reason="Room is full")
        return

    await manager.connect(websocket, room_id)

    join_message = {"type": "user_join", "user_id": user.id, "username": user.user}
    await manager.broadcast(join_message, room_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = {
                "type": "chat_message",
                "sender_id": user.id,
                "username": user.user,
                "content": data,
            }
            await manager.broadcast(message, room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        leave_message = {
            "type": "user_leave",
            "user_id": user.id,
            "username": user.user,
        }
        await manager.broadcast(leave_message, room_id)
