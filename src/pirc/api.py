# src/pirc/api.py
from fastapi import FastAPI, WebSocket
from pirc.core import PiRCCore
import uvicorn
import asyncio

app = FastAPI(title="PiRC Dashboard")
core = PiRCCore()

@app.get("/")
async def root():
    return {"message": "🚀 PiRC 0.1.0 Running", "loop_rate": 50}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_json({"status": "alive", "time": asyncio.current_task()})
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
