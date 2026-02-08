from __future__ import annotations

"""Adaptive learning / threshold management logic."""

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Tuple


@dataclass
class PerformanceWindow:
    contamination_rate: float
    conflict_rate: float
    avg_confidence: float
    sample_size: int


@dataclass
class ThresholdAdjustment:
    timestamp: datetime
    material_type: str
    old_threshold: float
    new_threshold: float
    reason: str


class AdaptiveThresholdManager:
    """Implements the rules described in the technical spec."""

    def __init__(self) -> None:
        self.thresholds: Dict[str, float] = {
            "PLASTIC": 0.75,
            "METAL": 0.75,
            "PAPER": 0.75,
            "GLASS": 0.75,
            "ORGANIC": 0.70,
        }
        self.min_threshold = 0.60
        self.max_threshold = 0.95
        self.adjustment_history: List[ThresholdAdjustment] = []
        self.events: Dict[str, Deque[Tuple[datetime, bool, bool, float]]] = defaultdict(
            lambda: deque(maxlen=2000)
        )

    def record_event(
        self,
        material_type: str,
        contamination_flag: bool,
        agent_disagreement: bool,
        confidence: float,
    ) -> None:
        key = material_type.upper()
        self.events[key].append((datetime.utcnow(), contamination_flag, agent_disagreement, confidence))

    def _window_metrics(self, material_type: str, window: timedelta) -> PerformanceWindow:
        now = datetime.utcnow()
        events = self.events.get(material_type.upper(), deque())
        window_events = [e for e in events if now - e[0] <= window]
        if not window_events:
            return PerformanceWindow(0.0, 0.0, 0.0, 0)

        total = len(window_events)
        contamination = sum(1 for _, c, _, _ in window_events if c)
        conflicts = sum(1 for _, _, a, _ in window_events if a)
        avg_conf = sum(conf for *_, conf in window_events) / total
        return PerformanceWindow(
            contamination_rate=round(contamination / total * 100, 2),
            conflict_rate=round(conflicts / total * 100, 2),
            avg_confidence=round(avg_conf * 100, 2),
            sample_size=total,
        )

    def is_stable_low_contamination(self, material_type: str, days: int = 7) -> bool:
        window = timedelta(days=days)
        metrics = self._window_metrics(material_type, window)
        return metrics.sample_size >= 200 and metrics.contamination_rate < 5

    def adjust_threshold(self, material_type: str) -> ThresholdAdjustment | None:
        metrics = self._window_metrics(material_type, timedelta(hours=12))
        current = self.thresholds[material_type]

        if metrics.sample_size == 0:
            return None

        if metrics.contamination_rate > 20:
            new_threshold = min(current + 0.05, self.max_threshold)
            reason = f"High contamination rate: {metrics.contamination_rate:.1f}%"
        elif metrics.contamination_rate < 5 and self.is_stable_low_contamination(material_type):
            new_threshold = max(current - 0.02, self.min_threshold)
            reason = f"Stable low contamination: {metrics.contamination_rate:.1f}%"
        elif metrics.conflict_rate > 25:
            new_threshold = self.max_threshold
            reason = f"High agent conflict rate: {metrics.conflict_rate:.1f}%"
        else:
            new_threshold = current
            reason = "No adjustment needed"

        if new_threshold == current:
            return None

        adjustment = ThresholdAdjustment(
            timestamp=datetime.utcnow(),
            material_type=material_type,
            old_threshold=current,
            new_threshold=new_threshold,
            reason=reason,
        )
        self.thresholds[material_type] = new_threshold
        self.adjustment_history.append(adjustment)
        return adjustment

    def analyze_all(self) -> List[ThresholdAdjustment]:
        adjustments: List[ThresholdAdjustment] = []
        for material in list(self.thresholds.keys()):
            adj = self.adjust_threshold(material)
            if adj:
                adjustments.append(adj)
        return adjustments

    def snapshot(self) -> Dict[str, object]:
        window = timedelta(hours=12)
        perf = {
            material: self._window_metrics(material, window)
            for material in self.thresholds.keys()
        }
        return {
            "thresholds": self.thresholds,
            "performance": {m: perf[m].__dict__ for m in perf},
            "adjustments": [
                {
                    "timestamp": adj.timestamp.isoformat(),
                    "material_type": adj.material_type,
                    "old_threshold": adj.old_threshold,
                    "new_threshold": adj.new_threshold,
                    "reason": adj.reason,
                }
                for adj in self.adjustment_history[-20:]
            ],
        }
