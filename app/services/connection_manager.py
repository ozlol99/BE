import json
from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket, status


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, Dict[int, WebSocket]] = defaultdict(dict)
        self.history: Dict[str, List[dict]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room_id: str, user_id: int):
        await websocket.accept()
        self.active_connections[room_id][user_id] = websocket

        # Send chat history to the newly connected user
        if room_id in self.history:
            for message in self.history[room_id]:
                await websocket.send_text(json.dumps(message))

    def disconnect(self, room_id: str, user_id: int):
        if (
            room_id in self.active_connections
            and user_id in self.active_connections[room_id]
        ):
            del self.active_connections[room_id][user_id]
            # If the room is empty, clear the connection and history
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                if room_id in self.history:
                    del self.history[room_id]

    async def disconnect_user(self, room_id: str, user_id: int):
        if (
            room_id in self.active_connections
            and user_id in self.active_connections[room_id]
        ):
            websocket = self.active_connections[room_id][user_id]
            await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
            self.disconnect(room_id, user_id)

    async def broadcast(self, message: dict, room_id: str, save_to_history: bool = True):
        # Store message in history if requested
        if save_to_history:
            self.history[room_id].append(message)

        if room_id in self.active_connections:
            message_str = json.dumps(message, ensure_ascii=False)
            for user_id, connection in self.active_connections[room_id].items():
                await connection.send_text(message_str)

    def get_active_user_count(self, room_id: str) -> int:
        if room_id in self.active_connections:
            return len(self.active_connections[room_id])
        return 0


manager = ConnectionManager()
