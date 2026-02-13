from __future__ import annotations

import random
import time
import uuid

from .schemas import Detection, Decision, Event

LABELS = [
    "plastic",
    "glass",
    "metal",
    "paper",
    "cardboard",
    "organic",
    "food",
    "battery",
    "chemical",
    "trash",
]

ROUTES = ["PLASTIC_BIN", "PAPER_BIN", "GLASS_BIN", "METAL_BIN", "ORGANIC", "HAZARDOUS", "LANDFILL"]


def random_detection() -> Detection:
    label = random.choice(LABELS)
    confidence = round(random.uniform(0.72, 0.99), 2)
    bbox = [
        round(random.uniform(0.05, 0.7), 2),
        round(random.uniform(0.05, 0.7), 2),
        round(random.uniform(0.1, 0.3), 2),
        round(random.uniform(0.1, 0.3), 2),
    ]
    return Detection(label=label, confidence=confidence, bbox=bbox)


def generate_event() -> Event:
    """Generate simulated event without requiring inference pipeline."""
    detection = random_detection()
    
    # Simple route mapping for simulation
    route_map = {
        "plastic": "PLASTIC_BIN",
        "glass": "GLASS_BIN",
        "metal": "METAL_BIN",
        "paper": "PAPER_BIN",
        "cardboard": "PAPER_BIN",
        "organic": "ORGANIC",
        "food": "ORGANIC",
        "battery": "HAZARDOUS",
        "chemical": "HAZARDOUS",
        "trash": "LANDFILL",
    }
    
    route = route_map.get(detection.label, random.choice(ROUTES))
    
    # 20% agent disagreement for simulation
    agent_disagreement = random.random() < 0.2
    contamination_flag = agent_disagreement and random.random() < 0.5
    
    confidence_score = detection.confidence * (0.8 if agent_disagreement else 1.0)
    contamination_score = random.uniform(0.3, 0.7) if contamination_flag else 0.0
    
    reason = None
    if agent_disagreement:
        reason = "Simulated agent disagreement"
    elif contamination_flag:
        reason = "Simulated contamination detected"

    return Event(
        id=str(uuid.uuid4()),
        ts=int(time.time()),
        detection=detection,
        decision=Decision(
            route=route,
            contamination_flag=contamination_flag,
            agent_disagreement=agent_disagreement,
            reason=reason,
            contamination_score=contamination_score,
            confidence_score=confidence_score,
            material_agent_decision=detection.label,
            routing_agent_decision=detection.label if not agent_disagreement else random.choice(LABELS),
        ),
    )
