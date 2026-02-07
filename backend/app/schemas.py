from __future__ import annotations

from pydantic import BaseModel, Field


class Detection(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[float]  # [x, y, w, h]


class Decision(BaseModel):
    route: str
    contamination_flag: bool
    agent_disagreement: bool
    reason: str | None = None


class Event(BaseModel):
    id: str
    ts: float
    detection: Detection
    decision: Decision


class Metrics(BaseModel):
    items_processed: int
    contamination_alerts: int
    system_accuracy: float
    efficiency_score: float
    co2_saved_kg: float
    recovery_value_usd: float
