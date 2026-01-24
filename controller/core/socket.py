from fastapi import WebSocket
from typing import List, Dict
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Send current module states (e.g., Vision process sync)
        from core.manager import module_manager
        for name, module in module_manager.modules.items():
            if hasattr(module, 'get_state'):
                state = module.get_state()
                await self.send_personal_message({
                    "type": f"{name}_update",
                    "data": state
                }, websocket)

        # Send log history to the newly connected client
        if module_manager.log_history:
            for log in reversed(module_manager.log_history):
                await self.send_personal_message({
                    "type": "notification",
                    "data": {
                        "message": log["message"],
                        "level": log["level"],
                        "time": log["time"]
                    }
                }, websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

socket_manager = ConnectionManager()
