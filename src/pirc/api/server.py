# src/pirc/api/server.py
from fastapi import FastAPI, WebSocket
from pirc.tge.fsm import RobotState
import prometheus_client

app = FastAPI(title="PiRC Robot API")
metrics = prometheus_client.REGISTRY

@app.websocket("/ws/robot")
async def robot_websocket(websocket: WebSocket):
    await websocket.accept()
    while True:
        state = await get_robot_state()  # 50Hz FSM state
        await websocket.send_json(state)
        await asyncio.sleep(0.02)

@app.get("/metrics")
async def prometheus():
    return prometheus_client.generate_latest()
