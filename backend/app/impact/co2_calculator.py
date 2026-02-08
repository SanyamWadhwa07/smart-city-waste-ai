from __future__ import annotations

"""CO₂ impact calculations for CogniRecycle."""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class EmissionFactors:
    """Kg CO₂ saved per kg of material recycled/composted."""

    plastic: float = 1.5
    paper: float = 0.9
    metal_aluminum: float = 9.0
    metal_steel: float = 1.5
    glass: float = 0.5
    organic: float = 0.3


class CO2Calculator:
    """Encapsulates CO₂ savings estimation."""

    EMISSION_FACTORS: Dict[str, float] = {
        "PLASTIC": EmissionFactors().plastic,
        "PAPER": EmissionFactors().paper,
        "METAL_ALUMINUM": EmissionFactors().metal_aluminum,
        "METAL_STEEL": EmissionFactors().metal_steel,
        "GLASS": EmissionFactors().glass,
        "ORGANIC": EmissionFactors().organic,
    }

    # Average weight per item in kilograms
    AVERAGE_WEIGHTS: Dict[str, float] = {
        "plastic_bottle": 0.015,
        "plastic_container": 0.050,
        "aluminum_can": 0.015,
        "steel_can": 0.030,
        "glass_bottle": 0.300,
        "cardboard": 0.100,
        "newspaper": 0.050,
        "food_scrap": 0.150,
    }

    # Map incoming labels to material categories used by emission factors
    MATERIAL_MAP: Dict[str, str] = {
        "plastic": "PLASTIC",
        "paper": "PAPER",
        "cardboard": "PAPER",
        "metal": "METAL_STEEL",
        "aluminum": "METAL_ALUMINUM",
        "aluminum_can": "METAL_ALUMINUM",
        "steel": "METAL_STEEL",
        "glass": "GLASS",
        "organic": "ORGANIC",
        "food": "ORGANIC",
    }

    def get_material_type(self, object_class: str) -> str:
        key = object_class.lower()
        return self.MATERIAL_MAP.get(key, key.upper())

    def calculate_item_co2_savings(self, object_class: str, routing_decision: str) -> float:
        """
        Calculate CO₂ saved for a single routed item.
        """
        if routing_decision.upper() not in {"RECYCLABLE", "ORGANIC"}:
            return 0.0

        material = self.get_material_type(object_class)
        emission_factor = self.EMISSION_FACTORS.get(material, 0.0)

        weight_key = object_class.lower().replace(" ", "_")
        weight_kg = self.AVERAGE_WEIGHTS.get(weight_key, 0.05)  # default 50g

        co2_saved = weight_kg * emission_factor
        return round(co2_saved, 4)

    def calculate_batch_prevention_bonus(self, contamination_prevented: int) -> float:
        """
        Each prevented contaminated batch saves ~25 kg recyclables at ~1.5 kg CO₂/kg.
        """
        avg_batch_weight = 25.0  # kg
        avg_emission_factor = 1.5
        return round(contamination_prevented * avg_batch_weight * avg_emission_factor, 2)
