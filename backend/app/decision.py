from __future__ import annotations

from dataclasses import dataclass


ROUTES = {
    "plastic": "Recyclable",
    "glass": "Recyclable",
    "metal": "Recyclable",
    "paper": "Recyclable",
    "cardboard": "Recyclable",
    "organic": "Organic",
    "food": "Organic",
    "battery": "Hazardous",
    "chemical": "Hazardous",
    "trash": "Landfill",
}

HAZARDOUS = {"battery", "chemical"}


@dataclass
class DecisionResult:
    route: str
    contamination_flag: bool
    agent_disagreement: bool
    reason: str | None = None


def decide(label: str, confidence: float, agent_b_label: str | None = None) -> DecisionResult:
    route = ROUTES.get(label, "Landfill")
    contamination_flag = False
    agent_disagreement = False
    reason = None

    if label in HAZARDOUS:
        contamination_flag = True
        reason = "hazardous_item"

    if agent_b_label and agent_b_label != label:
        agent_disagreement = True
        contamination_flag = True
        reason = "agent_disagreement"

    if confidence < 0.75:
        contamination_flag = True
        reason = reason or "low_confidence"

    return DecisionResult(
        route=route,
        contamination_flag=contamination_flag,
        agent_disagreement=agent_disagreement,
        reason=reason,
    )
