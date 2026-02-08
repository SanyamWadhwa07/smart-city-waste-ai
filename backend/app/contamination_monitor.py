from __future__ import annotations

"""Contamination prevention module (Feature 3)."""

from collections import deque, Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Tuple

from .schemas import Event


@dataclass
class WindowMetrics:
    total: int
    contamination_rate: float
    conflict_rate: float
    low_confidence_rate: float
    material_breakdown: Dict[str, int]


class ContaminationMonitor:
    def __init__(self):
        self.events: Deque[Tuple[datetime, Event]] = deque(maxlen=5000)
        self.low_conf_threshold = 0.7

    def record(self, event: Event) -> None:
        self.events.append((datetime.utcnow(), event))

    def _slice(self, limit: int | None = None, window: timedelta | None = None) -> List[Event]:
        now = datetime.utcnow()
        result: List[Event] = []
        for ts, evt in reversed(self.events):
            if window and now - ts > window:
                break
            result.append(evt)
            if limit and len(result) >= limit:
                break
        return list(reversed(result))

    def window_metrics(self, limit: int | None = None, window: timedelta | None = None) -> WindowMetrics:
        events = self._slice(limit=limit, window=window)
        total = len(events) or 1
        contamination = sum(1 for e in events if e.decision.contamination_flag)
        conflicts = sum(1 for e in events if e.decision.agent_disagreement)
        low_conf = sum(1 for e in events if e.detection.confidence < self.low_conf_threshold)
        breakdown = Counter(e.detection.label.upper() for e in events)
        return WindowMetrics(
            total=len(events),
            contamination_rate=round(contamination / total * 100, 2),
            conflict_rate=round(conflicts / total * 100, 2),
            low_confidence_rate=round(low_conf / total * 100, 2),
            material_breakdown=dict(breakdown),
        )

    def metrics_payload(self) -> Dict[str, dict]:
        short = self.window_metrics(limit=100)
        medium = self.window_metrics(window=timedelta(hours=1))
        long = self.window_metrics(window=timedelta(hours=24))
        return {
            "short_term": short.__dict__,
            "medium_term": medium.__dict__,
            "long_term": long.__dict__,
        }

    def generate_alerts(self) -> List[dict]:
        alerts: List[dict] = []
        short = self.window_metrics(limit=100)
        long = self.window_metrics(window=timedelta(hours=24))

        def make(level: str, title: str, msg: str, metric: float):
            alerts.append(
                {
                    "id": f"alert-{len(alerts)+1}",
                    "type": level,
                    "title": title,
                    "message": msg,
                    "currentRate": metric,
                    "historicalRate": long.contamination_rate,
                    "timestamp": datetime.utcnow().isoformat(),
                    "resolved": False,
                }
            )

        if short.contamination_rate >= 25:
            make("critical", "Contamination spike", "Rolling 100 items exceed 25%", short.contamination_rate)
        elif short.contamination_rate >= 15:
            make("warning", "Contamination rising", "Rolling 100 items exceed 15%", short.contamination_rate)

        if short.conflict_rate >= 20:
            make("warning", "Agent conflicts elevated", "Dual-agent conflicts exceed 20%", short.conflict_rate)

        if short.low_confidence_rate >= 15:
            make("info", "Low confidence streak", "Multiple low-confidence detections observed", short.low_confidence_rate)

        # Hazardous item misrouted
        for _, evt in list(self.events)[-50:]:
            if "battery" in evt.detection.label.lower() and evt.decision.route != "HAZARDOUS":
                make("critical", "Hazardous in wrong stream", "Battery detected outside hazardous stream", 100.0)
                break

        return alerts
