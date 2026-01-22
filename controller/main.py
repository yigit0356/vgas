import asyncio
import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import modules
from core.manager import module_manager
from core.socket import socket_manager

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await module_manager.load_modules(modules)
    await module_manager.start_all()
    yield
    # Shutdown (if needed)

app = FastAPI(title="VGAS Controller", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/config")
async def get_config():
    config_module = module_manager.modules.get("config")
    if config_module:
        return config_module.config
    return {"error": "Config module not found"}

@app.post("/config")
async def update_config(config: dict):
    config_module = module_manager.modules.get("config")
    if config_module:
        updated = config_module.save_config(config)
        await module_manager.send_notification("Configuration updated successfully", "success")
        return updated
    return {"error": "Config module not found"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await socket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
    except WebSocketDisconnect:
        socket_manager.disconnect(websocket)

# Serve the Dashboard
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# Mount static files (if any other assets exist)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
