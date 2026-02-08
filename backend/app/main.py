from __future__ import annotations

import asyncio
import os
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .schemas import Event, ImpactSummary, Metrics, ThresholdSnapshot
from .simulator import generate_event
from .impact import ImpactTracker
from .adaptive import AdaptiveThresholdManager

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

impact_tracker = ImpactTracker()
adaptive_manager = AdaptiveThresholdManager()

def update_metrics(event: Event) -> None:
    _state["items_processed"] += 1
    if event.decision.contamination_flag:
        _state["contamination_alerts"] += 1

    # Environmental & economic impact
    impact_tracker.record_event(
        object_class=event.detection.label,
        routing_decision=event.decision.route,
        contaminated=event.decision.contamination_flag,
        agent_disagreement=event.decision.agent_disagreement,
    )
    snap = impact_tracker.summary()
    _state["co2_saved_kg"] = snap.total_co2_kg
    _state["recovery_value_usd"] = snap.revenue_usd

    # Adaptive learning tracking
    adaptive_manager.record_event(
        material_type=event.detection.label,
        contamination_flag=event.decision.contamination_flag,
        agent_disagreement=event.decision.agent_disagreement,
        confidence=event.detection.confidence,
    )

    # Core operational metrics remain stochastic for demo purposes
    _state["system_accuracy"] = round(0.92 + random.random() * 0.06, 2)
    _state["efficiency_score"] = round(0.75 + random.random() * 0.2, 2)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics", response_model=Metrics)
async def metrics():
    return Metrics(**_state)


@app.get("/impact/summary", response_model=ImpactSummary)
async def impact_summary():
    snap = impact_tracker.summary()
    history = [
        {"ts": ts, "co2_saved": co2, "revenue": rev} for ts, co2, rev in snap.history
    ]
    return ImpactSummary(
        total_co2_kg=snap.total_co2_kg,
        revenue_usd=snap.revenue_usd,
        contamination_prevented=snap.contamination_prevented,
        by_material_co2=snap.by_material_co2,
        history=history,
        last_updated=snap.last_updated.isoformat(),
    )


@app.get("/learning/thresholds", response_model=ThresholdSnapshot)
async def learning_snapshot():
    return adaptive_manager.snapshot()


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
                    update_metrics(event)
                    await ws.send_json(event.model_dump())
                    await asyncio.sleep(0.02)
            finally:
                inference.close()
        else:
            while True:
                event = generate_event()
                update_metrics(event)
                await ws.send_json(event.model_dump())
                await asyncio.sleep(random.uniform(0.8, 1.6))
    except WebSocketDisconnect:
        return
