from __future__ import annotations

"""Adaptive Learning System (Feature 5)."""

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Tuple


@dataclass
class ThresholdAdjustment:
    timestamp: datetime
    material_type: str
    old_threshold: float
    new_threshold: float
    reason: str


@dataclass
class MaterialPerformance:
    total_events: int
    contaminations: int
    conflicts: int
    avg_confidence: float

    @property
    def contamination_rate(self) -> float:
        return (self.contaminations / self.total_events * 100) if self.total_events > 0 else 0.0

    @property
    def conflict_rate(self) -> float:
        return (self.conflicts / self.total_events * 100) if self.total_events > 0 else 0.0


class AdaptiveThresholdManager:
    """
    Dynamically adjust confidence thresholds and routing rules based on performance.
    Implements self-improving feedback loops.
    """

    MIN_THRESHOLD = 0.60
    MAX_THRESHOLD = 0.95
    DEFAULT_THRESHOLD = 0.75

    def __init__(self):
        # Per-material confidence thresholds
        self.thresholds: Dict[str, float] = defaultdict(lambda: self.DEFAULT_THRESHOLD)
        
        # Performance tracking (material_type -> deque of events)
        self.events: Dict[str, Deque[Tuple[datetime, dict]]] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        
        # Adjustment history
        self.adjustments: List[ThresholdAdjustment] = []
        
        # Pattern detection
        self.false_positives: Dict[str, int] = defaultdict(int)
        self.last_adjustment: Dict[str, datetime] = {}

    def record_event(
        self,
        material_type: str,
        contamination_flag: bool,
        agent_disagreement: bool,
        confidence: float,
    ) -> None:
        """Record an event for performance analysis."""
        event = {
            "timestamp": datetime.utcnow(),
            "contaminated": contamination_flag,
            "conflict": agent_disagreement,
            "confidence": confidence,
        }
        
        mat = material_type.upper()
        self.events[mat].append((datetime.utcnow(), event))
        
        # Check if adjustment needed (every 500 events)
        if len(self.events[mat]) % 500 == 0:
            self._maybe_adjust_threshold(mat)

    def _get_performance(self, material_type: str, window_size: int = 500) -> MaterialPerformance:
        """Analyze recent performance for material type."""
        events = list(self.events[material_type])[-window_size:]
        
        if not events:
            return MaterialPerformance(0, 0, 0, 0.0)
        
        total = len(events)
        contaminations = sum(1 for _, e in events if e["contaminated"])
        conflicts = sum(1 for _, e in events if e["conflict"])
        avg_conf = sum(e["confidence"] for _, e in events) / total
        
        return MaterialPerformance(total, contaminations, conflicts, avg_conf)

    def _maybe_adjust_threshold(self, material_type: str) -> None:
        """Check if threshold adjustment is needed based on performance."""
        perf = self._get_performance(material_type)
        
        if perf.total_events < 100:
            return  # Not enough data
        
        current_threshold = self.thresholds[material_type]
        new_threshold = current_threshold
        reason = ""
        
        # Scenario 1: High contamination rate -> increase threshold
        if perf.contamination_rate > 20:
            new_threshold = min(current_threshold + 0.05, self.MAX_THRESHOLD)
            reason = f"High contamination rate: {perf.contamination_rate:.1f}%"
        
        # Scenario 2: Very low contamination + stable -> decrease threshold
        elif perf.contamination_rate < 5 and self._is_stable_low_contamination(material_type):
            new_threshold = max(current_threshold - 0.02, self.MIN_THRESHOLD)
            reason = f"Stable low contamination: {perf.contamination_rate:.1f}%"
        
        # Scenario 3: High conflict rate -> increase threshold (uncertain)
        elif perf.conflict_rate > 25:
            new_threshold = min(current_threshold + 0.10, self.MAX_THRESHOLD)
            reason = f"High agent conflict rate: {perf.conflict_rate:.1f}%"
        
        # Apply adjustment if changed
        if new_threshold != current_threshold:
            # Cooldown: Don't adjust same material too frequently
            last_adj = self.last_adjustment.get(material_type)
            if last_adj and datetime.utcnow() - last_adj < timedelta(hours=1):
                return  # Too soon
            
            self._apply_adjustment(material_type, current_threshold, new_threshold, reason)

    def _is_stable_low_contamination(self, material_type: str, days: int = 7) -> bool:
        """Check if contamination has been stable and low for N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        events = [
            e for ts, e in self.events[material_type]
            if ts >= cutoff
        ]
        
        if len(events) < 200:
            return False  # Not enough data
        
        # Check daily contamination rates
        daily_rates = []
        for day in range(days):
            start = datetime.utcnow() - timedelta(days=day+1)
            end = datetime.utcnow() - timedelta(days=day)
            
            day_events = [e for ts, e in self.events[material_type] if start <= ts < end]
            if not day_events:
                continue
            
            contaminated = sum(1 for e in day_events if e["contaminated"])
            rate = contaminated / len(day_events) * 100
            daily_rates.append(rate)
        
        # All days below 5%?
        return len(daily_rates) >= days and all(r < 5 for r in daily_rates)

    def _apply_adjustment(
        self,
        material_type: str,
        old_threshold: float,
        new_threshold: float,
        reason: str,
    ) -> None:
        """Apply threshold adjustment and log it."""
        self.thresholds[material_type] = new_threshold
        self.last_adjustment[material_type] = datetime.utcnow()
        
        adjustment = ThresholdAdjustment(
            timestamp=datetime.utcnow(),
            material_type=material_type,
            old_threshold=round(old_threshold, 2),
            new_threshold=round(new_threshold, 2),
            reason=reason,
        )
        
        self.adjustments.append(adjustment)
        
        # Keep last 100 adjustments
        if len(self.adjustments) > 100:
            self.adjustments.pop(0)

    def get_threshold(self, material_type: str) -> float:
        """Get current threshold for material type."""
        return self.thresholds.get(material_type.upper(), self.DEFAULT_THRESHOLD)

    def get_recent_adjustments(self, limit: int = 10) -> List[dict]:
        """Get recent threshold adjustments."""
        recent = self.adjustments[-limit:]
        return [
            {
                "timestamp": adj.timestamp.isoformat(),
                "material_type": adj.material_type,
                "old_threshold": adj.old_threshold,
                "new_threshold": adj.new_threshold,
                "reason": adj.reason,
            }
            for adj in reversed(recent)
        ]

    def get_performance_report(self) -> Dict[str, dict]:
        """Generate performance report for all materials."""
        report = {}
        for material_type in self.events.keys():
            perf = self._get_performance(material_type)
            report[material_type] = {
                "total_events": perf.total_events,
                "contamination_rate": round(perf.contamination_rate, 2),
                "conflict_rate": round(perf.conflict_rate, 2),
                "avg_confidence": round(perf.avg_confidence, 2),
                "current_threshold": round(self.thresholds[material_type], 2),
            }
        return report
