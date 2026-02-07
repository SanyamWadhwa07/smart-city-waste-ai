from __future__ import annotations

import asyncio
import os
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .schemas import Metrics
from .simulator import generate_event

USE_REAL_INFERENCE = os.getenv("USE_REAL_INFERENCE", "0") == "1"

try:
    from .inference import load_inference_from_env
except Exception:
    load_inference_from_env = None

app = FastAPI(title="CogniRecycle Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_state = {
    "items_processed": 0,
    "contamination_alerts": 0,
    "system_accuracy": 0.95,
    "efficiency_score": 0.82,
    "co2_saved_kg": 0.0,
    "recovery_value_usd": 0.0,
}


def update_metrics(event_contamination: bool) -> None:
    _state["items_processed"] += 1
    if event_contamination:
        _state["contamination_alerts"] += 1
    _state["co2_saved_kg"] = round(_state["items_processed"] * 0.0035, 2)
    _state["recovery_value_usd"] = round(_state["items_processed"] * 0.18, 2)
    _state["system_accuracy"] = round(0.92 + random.random() * 0.06, 2)
    _state["efficiency_score"] = round(0.75 + random.random() * 0.2, 2)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics", response_model=Metrics)
async def metrics():
    return Metrics(**_state)


@app.websocket("/ws/detections")
async def detections(ws: WebSocket):
    await ws.accept()
    try:
        if USE_REAL_INFERENCE and load_inference_from_env:
            inference = load_inference_from_env()
            try:
                while True:
                    event = inference.next_event()
                    if event is None:
                        await asyncio.sleep(0.05)
                        continue
                    update_metrics(event.decision.contamination_flag)
                    await ws.send_json(event.model_dump())
                    await asyncio.sleep(0.02)
            finally:
                inference.close()
        else:
            while True:
                event = generate_event()
                update_metrics(event.decision.contamination_flag)
                await ws.send_json(event.model_dump())
                await asyncio.sleep(random.uniform(0.8, 1.6))
    except WebSocketDisconnect:
        return
