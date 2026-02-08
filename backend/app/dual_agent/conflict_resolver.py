from __future__ import annotations

"""Conflict resolution between material and routing agents."""

from typing import Tuple


class ConflictResolver:
    def resolve(self, material_route: str, routing_route: str, contamination_score: float) -> Tuple[str, bool, str]:
        if material_route == routing_route:
            return routing_route, False, "agents_agree"

        # conflict detected
        if contamination_score > 0.7:
            return "LANDFILL", True, "high_contamination_conflict"
        if contamination_score > 0.4:
            return "MANUAL_REVIEW", True, "uncertain_conflict"
        return material_route, True, "low_confidence_conflict"
