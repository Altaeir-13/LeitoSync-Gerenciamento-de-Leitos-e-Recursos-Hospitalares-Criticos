import json
from typing import List
from fastapi import WebSocket
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_resource_update(self, resource_id: int, new_status: str):
        message = {
            "type": "RESOURCE_UPDATED",
            "resource_id": resource_id,
            "new_status": new_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()
