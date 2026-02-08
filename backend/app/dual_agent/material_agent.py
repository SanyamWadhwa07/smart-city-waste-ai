from __future__ import annotations

"""Material agent: maps YOLO labels to material categories."""

from typing import Dict

MATERIAL_MAPPING: Dict[str, str] = {
    # Plastics
    "plastic_bottle": "PLASTIC",
    "plastic_container": "PLASTIC",
    "plastic_bag": "PLASTIC",
    "plastic_film": "PLASTIC",
    # Metals
    "aluminum_can": "METAL",
    "steel_can": "METAL",
    "metal_scrap": "METAL",
    # Paper products
    "cardboard": "PAPER",
    "newspaper": "PAPER",
    "magazine": "PAPER",
    "office_paper": "PAPER",
    "paper": "PAPER",
    # Glass
    "glass_bottle": "GLASS",
    "glass_jar": "GLASS",
    "glass": "GLASS",
    # Organic
    "food_scrap": "ORGANIC",
    "fruit_peel": "ORGANIC",
    "vegetable_waste": "ORGANIC",
    "organic": "ORGANIC",
    "food": "ORGANIC",
    # E-waste
    "battery": "E_WASTE",
    "electronics": "E_WASTE",
    "circuit_board": "E_WASTE",
    # Textiles
    "clothing": "TEXTILE",
    "fabric": "TEXTILE",
    "textile": "TEXTILE",
}


class MaterialAgent:
    def classify(self, label: str) -> str:
        return MATERIAL_MAPPING.get(label.lower(), "UNKNOWN")
