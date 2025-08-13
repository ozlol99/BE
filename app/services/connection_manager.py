import json
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # { "room_id": [WebSocket, WebSocket, ...] }
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if (
            room_id in self.active_connections
            and websocket in self.active_connections[room_id]
        ):
            self.active_connections[room_id].remove(websocket)
            # 방에 아무도 없으면 방 목록에서 제거
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(json.dumps(message))

    def get_active_user_count(self, room_id: str) -> int:
        if room_id in self.active_connections:
            return len(self.active_connections[room_id])
        return 0


manager = ConnectionManager()
