import json
from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.history: Dict[str, List[dict]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)

        # Send chat history to the newly connected user
        if room_id in self.history:
            for message in self.history[room_id]:
                await websocket.send_text(json.dumps(message))

    def disconnect(self, websocket: WebSocket, room_id: str):
        if (
            room_id in self.active_connections
            and websocket in self.active_connections[room_id]
        ):
            self.active_connections[room_id].remove(websocket)
            # If the room is empty, clear the connection and history
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                if room_id in self.history:
                    del self.history[room_id]

    async def broadcast(self, message: dict, room_id: str):
        # Store message in history before broadcasting
        self.history[room_id].append(message)

        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(json.dumps(message))

    def get_active_user_count(self, room_id: str) -> int:
        if room_id in self.active_connections:
            return len(self.active_connections[room_id])
        return 0


manager = ConnectionManager()
