from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .dual_agent.dual_agent import DualAgentEngine, DualAgentDecision


@dataclass
class DecisionResult:
    route: str
    contamination_flag: bool
    agent_disagreement: bool
    reason: str | None = None
    contamination_score: float | None = None
    confidence_score: float | None = None
    material_agent_decision: str | None = None
    routing_agent_decision: str | None = None


_ENGINE: Optional[DualAgentEngine] = None


def _engine() -> DualAgentEngine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = DualAgentEngine(confidence_threshold=0.75)
    return _ENGINE


def decide(label: str, confidence: float, agent_b_label: str | None = None) -> DecisionResult:
    """Cross-validates material + routing agents and resolves conflicts."""
    decision: DualAgentDecision = _engine().run(label, confidence)

    agent_disagreement = decision.agent_disagreement
    reason = decision.reason

    # incorporate agent_b_label as synthetic conflict if provided
    if agent_b_label and agent_b_label.lower() != label.lower():
        agent_disagreement = True
        reason = "agent_b_conflict"

    return DecisionResult(
        route=decision.final_route,
        contamination_flag=decision.contamination_flag,
        agent_disagreement=agent_disagreement,
        reason=reason,
        contamination_score=decision.contamination_score,
        confidence_score=decision.confidence_score,
        material_agent_decision=decision.material_agent_decision,
        routing_agent_decision=decision.routing_agent_decision,
    )
