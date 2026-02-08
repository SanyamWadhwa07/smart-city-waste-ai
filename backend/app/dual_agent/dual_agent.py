from __future__ import annotations

"""Dual-agent orchestration (Feature 2)."""

from dataclasses import dataclass
from typing import Optional
import random

from .material_agent import MaterialAgent
from .routing_agent import RoutingAgent
from .conflict_resolver import ConflictResolver


@dataclass
class DualAgentDecision:
    final_route: str
    contamination_flag: bool
    agent_disagreement: bool
    reason: str
    contamination_score: float
    confidence_score: float
    material_agent_decision: str
    routing_agent_decision: str


class DualAgentEngine:
    def __init__(self, confidence_threshold: float = 0.75):
        self.material_agent = MaterialAgent()
        self.routing_agent = RoutingAgent(confidence_threshold=confidence_threshold)
        self.conflict_resolver = ConflictResolver()

    def run(self, label: str, confidence: float) -> DualAgentDecision:
        material = self.material_agent.classify(label)
        # Agent 1: material-based route suggestion
        material_route = self._material_route(material, label)

        # Agent 2: routing/contamination assessor
        routing_route, contamination_score, routing_reason = self.routing_agent.assess(
            material, label, confidence
        )

        final_route, conflict, conflict_reason = self.conflict_resolver.resolve(
            material_route, routing_route, contamination_score
        )

        contamination_flag = routing_route in {"LANDFILL", "HAZARDOUS"} or contamination_score >= 0.55

        return DualAgentDecision(
            final_route=final_route,
            contamination_flag=contamination_flag,
            agent_disagreement=conflict,
            reason=conflict_reason if conflict else routing_reason,
            contamination_score=contamination_score,
            confidence_score=confidence,
            material_agent_decision=material_route,
            routing_agent_decision=routing_route,
        )

    def _material_route(self, material: str, label: str) -> str:
        if material in {"PLASTIC", "PAPER", "GLASS", "METAL"}:
            return "RECYCLABLE"
        if material == "ORGANIC":
            return "ORGANIC"
        if material == "E_WASTE":
            return "HAZARDOUS"
        # Unknown: use small randomness to disperse between manual/landfill
        return "MANUAL_REVIEW" if random.random() < 0.5 else "LANDFILL"
