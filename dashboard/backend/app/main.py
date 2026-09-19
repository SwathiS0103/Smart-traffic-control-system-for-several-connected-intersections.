from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import json

from .adapters.adapter_manager import AdapterManager

app = FastAPI(title="Q-FLOW Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

adapter_manager = AdapterManager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.running = False
        self.task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

    async def run_simulation(self):
        while self.running:
            adapter_manager.step()
            state = adapter_manager.get_state()
            await self.broadcast({
                "type": "TRAFFIC_UPDATE",
                "state": state
            })
            await asyncio.sleep(1) # 1 update per second

manager = ConnectionManager()

@app.websocket("/ws/traffic")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_json({
            "type": "TRAFFIC_UPDATE",
            "state": adapter_manager.get_state()
        })
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/traffic/state")
def get_traffic_state():
    return adapter_manager.get_state()

@app.post("/api/simulation/start")
async def start_simulation():
    if not manager.running:
        manager.running = True
        manager.task = asyncio.create_task(manager.run_simulation())
    return {"status": "started"}

@app.post("/api/simulation/pause")
def pause_simulation():
    manager.running = False
    if manager.task:
        manager.task.cancel()
    return {"status": "paused"}

@app.post("/api/simulation/reset")
async def reset_simulation():
    adapter_manager.reset()
    state = adapter_manager.get_state()
    await manager.broadcast({
        "type": "TRAFFIC_UPDATE",
        "state": state
    })
    return {"status": "reset"}

@app.post("/api/simulation/scenario")
async def set_scenario(scenario: dict):
    name = scenario.get("name", "Normal Traffic")
    adapter_manager.set_scenario(name)
    state = adapter_manager.get_state()
    await manager.broadcast({
        "type": "TRAFFIC_UPDATE",
        "state": state
    })
    return {"status": "scenario_set", "scenario": name}
