from __future__ import annotations

"""Economic recovery estimation for CogniRecycle."""

from typing import Dict

from .co2_calculator import CO2Calculator


class RevenueEstimator:
    """Estimate revenue recovered from correctly routed materials."""

    MATERIAL_VALUES: Dict[str, float] = {
        "PLASTIC_PET": 0.40,
        "PLASTIC_HDPE": 0.35,
        "PLASTIC_MIXED": 0.15,
        "METAL_ALUMINUM": 0.80,
        "METAL_STEEL": 0.10,
        "PAPER_CARDBOARD": 0.08,
        "PAPER_MIXED": 0.05,
        "GLASS_CLEAR": 0.05,
        "GLASS_MIXED": 0.02,
    }

    CONTAMINATION_COST: Dict[str, float] = {
        "rejected_batch": -50.0,
        "contaminated_material": -0.10,
    }

    def __init__(self, co2_calculator: CO2Calculator | None = None) -> None:
        self.co2_calculator = co2_calculator or CO2Calculator()

    def map_to_value_category(self, object_class: str) -> str:
        key = object_class.lower()
        if "pet" in key:
            return "PLASTIC_PET"
        if "hdpe" in key:
            return "PLASTIC_HDPE"
        if "plastic" in key:
            return "PLASTIC_MIXED"
        if "aluminum" in key or "aluminium" in key:
            return "METAL_ALUMINUM"
        if "metal" in key or "steel" in key:
            return "METAL_STEEL"
        if "cardboard" in key:
            return "PAPER_CARDBOARD"
        if "paper" in key:
            return "PAPER_MIXED"
        if "glass" in key:
            return "GLASS_MIXED"
        return "PLASTIC_MIXED"

    def calculate_item_value(
        self, object_class: str, routing_decision: str, contaminated: bool = False
    ) -> float:
        """
        Calculate economic value for a single routed item.
        """
        if routing_decision.upper() != "RECYCLABLE" or contaminated:
            return 0.0

        material_category = self.map_to_value_category(object_class)
        weight_key = object_class.lower().replace(" ", "_")
        weight_kg = self.co2_calculator.AVERAGE_WEIGHTS.get(weight_key, 0.05)
        unit_value = self.MATERIAL_VALUES.get(material_category, 0.0)
        return round(weight_kg * unit_value, 4)

    def calculate_contamination_cost_avoided(self, contaminations_prevented: int) -> float:
        return round(
            contaminations_prevented * abs(self.CONTAMINATION_COST["rejected_batch"]), 2
        )
