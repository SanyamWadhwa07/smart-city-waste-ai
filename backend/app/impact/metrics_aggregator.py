from __future__ import annotations

"""Aggregates environmental and economic impact metrics."""

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Deque, Dict, List, Tuple

from .co2_calculator import CO2Calculator
from .revenue_estimator import RevenueEstimator


@dataclass
class ImpactSnapshot:
    total_co2_kg: float
    revenue_usd: float
    contamination_prevented: int
    by_material_co2: Dict[str, float]
    history: List[Tuple[str, float, float]]
    last_updated: datetime


class ImpactTracker:
    """Tracks running totals + short-term history for dashboarding."""

    def __init__(self) -> None:
        self.co2_calculator = CO2Calculator()
        self.revenue_estimator = RevenueEstimator(self.co2_calculator)
        self.total_co2 = 0.0
        self.total_revenue = 0.0
        self.contamination_prevented = 0
        self.by_material: Dict[str, float] = {}
        self.history: Deque[Tuple[datetime, float, float]] = deque(maxlen=500)

    def record_event(
        self,
        object_class: str,
        routing_decision: str,
        contaminated: bool,
        agent_disagreement: bool | None = None,
    ) -> None:
        routing = routing_decision.upper()
        co2_saved = self.co2_calculator.calculate_item_co2_savings(object_class, routing)
        revenue = self.revenue_estimator.calculate_item_value(
            object_class, routing, contaminated
        )

        material = self.co2_calculator.get_material_type(object_class)
        self.by_material[material] = round(self.by_material.get(material, 0.0) + co2_saved, 4)

        self.total_co2 = round(self.total_co2 + co2_saved, 4)
        self.total_revenue = round(self.total_revenue + revenue, 4)

        # Treat flagged contamination or agent disagreement as prevented contamination
        if contaminated or agent_disagreement:
            self.contamination_prevented += 1
            bonus = self.co2_calculator.calculate_batch_prevention_bonus(1)
            self.total_co2 = round(self.total_co2 + bonus, 4)

        now = datetime.utcnow()
        self.history.append((now, co2_saved, revenue))

    def summary(self) -> ImpactSnapshot:
        history_compact: List[Tuple[str, float, float]] = [
            (ts.isoformat(), co2, rev) for ts, co2, rev in list(self.history)
        ]
        return ImpactSnapshot(
            total_co2_kg=round(self.total_co2, 3),
            revenue_usd=round(self.total_revenue, 2),
            contamination_prevented=self.contamination_prevented,
            by_material_co2=self.by_material,
            history=history_compact,
            last_updated=datetime.utcnow(),
        )
