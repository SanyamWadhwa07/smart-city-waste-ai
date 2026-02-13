from __future__ import annotations

"""Environmental & Economic Impact Tracker (Feature 4)."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple


@dataclass
class ImpactSnapshot:
    total_co2_kg: float
    revenue_usd: float
    by_material_co2: Dict[str, float]
    by_material_revenue: Dict[str, float]
    contaminations_prevented: int
    history: List[Tuple[datetime, float, float]]


class ImpactTracker:
    """
    Calculate CO₂ savings and material recovery value.
    Based on EPA emission factors and recycled material market values.
    """

    # CO₂ emission factors (kg CO₂ saved per kg material recycled)
    EMISSION_FACTORS = {
        "PLASTIC": 1.5,
        "PAPER": 0.9,
        "CARDBOARD": 0.9,
        "METAL": 9.0,  # Aluminum
        "GLASS": 0.5,
        "ORGANIC": 0.3,
    }

    # Average item weights (kg)
    AVERAGE_WEIGHTS = {
        "plastic": 0.015,
        "plastic_bottle": 0.015,
        "plastic_container": 0.050,
        "plastic_bag": 0.005,
        "glass": 0.300,
        "glass_bottle": 0.300,
        "glass_jar": 0.250,
        "metal": 0.015,
        "aluminum_can": 0.015,
        "steel_can": 0.030,
        "paper": 0.050,
        "cardboard": 0.100,
        "newspaper": 0.050,
        "magazine": 0.080,
        "organic": 0.150,
        "food": 0.150,
        "food_scrap": 0.150,
        "battery": 0.020,
        "electronics": 0.100,
        "clothing": 0.200,
        "fabric": 0.100,
    }

    # Material market values (USD per kg)
    MATERIAL_VALUES = {
        "PLASTIC": 0.30,
        "PAPER": 0.05,
        "CARDBOARD": 0.08,
        "METAL": 0.80,  # Aluminum
        "GLASS": 0.04,
    }

    # Contamination prevention bonus
    BATCH_PREVENTION_VALUE = 50.0  # USD per prevented contamination
    BATCH_PREVENTION_CO2 = 37.5  # kg CO₂ per prevented batch

    def __init__(self):
        self.total_co2 = 0.0
        self.total_revenue = 0.0
        self.by_material_co2: Dict[str, float] = defaultdict(float)
        self.by_material_revenue: Dict[str, float] = defaultdict(float)
        self.contaminations_prevented = 0
        self.history: List[Tuple[datetime, float, float]] = []

    def _get_material_type(self, object_class: str) -> str:
        """Map object class to material type."""
        label = object_class.lower()
        if any(x in label for x in ["plastic", "bottle", "container", "bag"]):
            return "PLASTIC"
        elif any(x in label for x in ["paper", "newspaper", "magazine", "cardboard"]):
            if "cardboard" in label:
                return "CARDBOARD"
            return "PAPER"
        elif any(x in label for x in ["metal", "aluminum", "steel", "can"]):
            return "METAL"
        elif any(x in label for x in ["glass", "jar"]):
            return "GLASS"
        elif any(x in label for x in ["organic", "food", "fruit", "vegetable"]):
            return "ORGANIC"
        return "UNKNOWN"

    def _get_weight(self, object_class: str) -> float:
        """Get estimated weight for object class."""
        label = object_class.lower()
        return self.AVERAGE_WEIGHTS.get(label, 0.05)  # Default 50g

    def record_event(
        self,
        object_class: str,
        routing_decision: str,
        contaminated: bool,
        agent_disagreement: bool,
    ) -> None:
        """Record a detection event and update impact metrics."""
        
        # CO₂ savings (only for successfully recycled/composted items)
        if routing_decision in ["RECYCLABLE", "ORGANIC"] and not contaminated:
            material = self._get_material_type(object_class)
            weight_kg = self._get_weight(object_class)
            emission_factor = self.EMISSION_FACTORS.get(material, 0)
            
            co2_saved = weight_kg * emission_factor
            self.total_co2 += co2_saved
            self.by_material_co2[material] += co2_saved

        # Revenue recovery (only for recyclables)
        if routing_decision == "RECYCLABLE" and not contaminated:
            material = self._get_material_type(object_class)
            weight_kg = self._get_weight(object_class)
            unit_value = self.MATERIAL_VALUES.get(material, 0)
            
            revenue = weight_kg * unit_value
            self.total_revenue += revenue
            self.by_material_revenue[material] += revenue

        # Contamination prevention bonus
        if agent_disagreement and not contaminated:
            # Dual agents caught potential contamination
            self.contaminations_prevented += 1
            self.total_co2 += self.BATCH_PREVENTION_CO2
            self.total_revenue += self.BATCH_PREVENTION_VALUE

        # Record snapshot every 100 events for history
        if len(self.history) == 0 or len(self.history) % 100 == 0:
            self.history.append((datetime.utcnow(), self.total_co2, self.total_revenue))
            # Keep last 1000 snapshots
            if len(self.history) > 1000:
                self.history.pop(0)

    def summary(self) -> ImpactSnapshot:
        """Get current impact summary."""
        return ImpactSnapshot(
            total_co2_kg=round(self.total_co2, 2),
            revenue_usd=round(self.total_revenue, 2),
            by_material_co2={k: round(v, 2) for k, v in self.by_material_co2.items()},
            by_material_revenue={k: round(v, 2) for k, v in self.by_material_revenue.items()},
            contaminations_prevented=self.contaminations_prevented,
            history=self.history[-50:],  # Last 50 snapshots
        )

    def reset(self) -> None:
        """Reset all metrics (for testing)."""
        self.total_co2 = 0.0
        self.total_revenue = 0.0
        self.by_material_co2.clear()
        self.by_material_revenue.clear()
        self.contaminations_prevented = 0
        self.history.clear()
