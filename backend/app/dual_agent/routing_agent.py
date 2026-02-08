from __future__ import annotations

"""Routing agent: assesses recyclability/contamination and proposes bin route."""

import random
from typing import Tuple


class RoutingAgent:
    def __init__(self, confidence_threshold: float = 0.75):
        self.confidence_threshold = confidence_threshold

    def assess(self, material: str, label: str, confidence: float) -> Tuple[str, float, str]:
        """
        Returns (route, contamination_score, reason)
        """
        label_lower = label.lower()
        contamination_score = 0.0
        reason = "clean"

        if confidence < 0.6:
            return "MANUAL_REVIEW", 0.6, "very_low_confidence"

        # Hazardous handling
        if material in {"E_WASTE"} or "battery" in label_lower or "chemical" in label_lower:
            return "HAZARDOUS", 0.8, "hazardous_item"

        # Organic
        if material == "ORGANIC":
            return "ORGANIC", 0.2, "organic_stream"

        # Obvious contamination cues
        if "soiled" in label_lower or "dirty" in label_lower or "food" in label_lower:
            contamination_score = 0.75
            reason = "food_residue"
        if "mixed" in label_lower or "composite" in label_lower:
            contamination_score = max(contamination_score, 0.65)
            reason = "mixed_material"
        if confidence < self.confidence_threshold:
            contamination_score = max(contamination_score, 0.55)
            reason = "low_confidence"

        if material in {"PLASTIC", "PAPER", "GLASS", "METAL"}:
            if contamination_score >= 0.7:
                return "LANDFILL", contamination_score, reason
            if contamination_score >= 0.55:
                return "MANUAL_REVIEW", contamination_score, reason
            return "RECYCLABLE", contamination_score, "clean_recyclable"

        # Unknown defaults to manual review
        return "MANUAL_REVIEW", 0.4, "unknown_material"
