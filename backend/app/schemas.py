from __future__ import annotations

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List
import re


class Detection(BaseModel):
    label: str = Field(..., min_length=1, max_length=50)
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: list[float] = Field(..., min_items=4, max_items=4)  # [x, y, w, h]
    
    @validator('label')
    def validate_label(cls, v):
        if not v or not v.strip():
            raise ValueError("Label cannot be empty")
        # Sanitize label
        sanitized = v.strip()
        #Allow alphanumeric, spaces, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', sanitized):
            raise ValueError(f"Label contains invalid characters: {v}")
        return sanitized
    
    @validator('bbox')
    def validate_bbox(cls, v):
        if len(v) != 4:
            raise ValueError(f"BBox must have exactly 4 values, got {len(v)}")
        
        # Allow [0,0,0,0] for NO_DETECTION cases
        if v == [0.0, 0.0, 0.0, 0.0]:
            return v
        
        # Check all values are between 0 and 1 (normalized)
        for i, val in enumerate(v):
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"BBox value at index {i} must be normalized (0-1), got {val}")
        
        x, y, w, h = v
        # Check bbox doesn't extend beyond image bounds
        if x + w > 1.001 or y + h > 1.001:  # Small tolerance for floating point
            raise ValueError(f"BBox extends beyond image bounds: x+w={x+w}, y+h={y+h}")
        
        # Check bbox has positive area
        if w <= 0 or h <= 0:
            raise ValueError(f"BBox must have positive width and height, got w={w}, h={h}")
        
        return v


class Decision(BaseModel):
    route: str = Field(..., min_length=1, max_length=50)
    contamination_flag: bool
    agent_disagreement: bool
    reason: Optional[str] = Field(None, max_length=500)
    contamination_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    material_agent_decision: Optional[str] = Field(None, max_length=50)
    routing_agent_decision: Optional[str] = Field(None, max_length=50)
    
    @validator('route')
    def validate_route(cls, v):
        if not v or not v.strip():
            raise ValueError("Route cannot be empty")
        # Valid routes
        valid_routes = {
            "ORGANIC", "PLASTIC_BIN", "PAPER_BIN", "METAL_BIN", "GLASS_BIN",
            "HAZARDOUS", "LANDFILL", "MANUAL_REVIEW"
        }
        route_upper = v.strip().upper()
        if route_upper not in valid_routes:
            # Allow but log warning
            pass
        return v.strip()
    
    @validator('reason')
    def validate_reason(cls, v):
        if v:
            # Sanitize reason string
            return re.sub(r'[\x00-\x1f\x7f]', '', v.strip())[:500]
        return v


class Event(BaseModel):
    id: str = Field(..., min_length=1, max_length=100)
    ts: float = Field(..., gt=0)
    detection: Detection
    decision: Decision
    frame: Optional[str] = None  # Base64 encoded frame
    
    @validator('id')
    def validate_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Event ID cannot be empty")
        # Sanitize ID - allow only alphanumeric, dash, underscore
        sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', v.strip())
        if not sanitized:
            raise ValueError("Event ID must contain alphanumeric characters")
        return sanitized
    
    @validator('ts')
    def validate_timestamp(cls, v):
        # Reasonable timestamp range: 2020-2050
        MIN_TS = 1577836800  # 2020-01-01
        MAX_TS = 2556144000  # 2050-12-31
        if not MIN_TS <= v <= MAX_TS:
            raise ValueError(f"Timestamp out of reasonable range: {v}")
        return v


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


class WindowMetrics(BaseModel):
    total: int
    contamination_rate: float
    conflict_rate: float
    low_confidence_rate: float
    material_breakdown: dict[str, int]


class ContaminationMetricsResponse(BaseModel):
    short_term: WindowMetrics
    medium_term: WindowMetrics
    long_term: WindowMetrics


class AlertResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    currentRate: float
    historicalRate: float
    timestamp: str
    resolved: bool


class ReviewQueueItem(BaseModel):
    """Item flagged for manual review with full context."""
    event_id: str
    timestamp: str
    detection: Detection
    decision: Decision
    reason: str
    status: str = "pending"  # pending, approved, rejected
    reviewed_by: str | None = None
    reviewed_at: str | None = None


class ReviewQueueResponse(BaseModel):
    items: list[ReviewQueueItem]
    total: int
    pending: int
    reviewed: int
