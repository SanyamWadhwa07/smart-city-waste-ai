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


class ImpactHistoryPoint(BaseModel):
    ts: str
    co2_saved: float
    revenue: float


class ImpactSummary(BaseModel):
    total_co2_kg: float
    revenue_usd: float
    contamination_prevented: int
    by_material_co2: dict[str, float]
    history: list[ImpactHistoryPoint]
    last_updated: str


class ThresholdSnapshot(BaseModel):
    thresholds: dict[str, float]
    performance: dict
    adjustments: list[dict]
