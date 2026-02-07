from __future__ import annotations

import random
import time
import uuid

from .decision import decide
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


def random_agent_b_label(label: str) -> str | None:
    if random.random() < 0.2:
        return random.choice([l for l in LABELS if l != label])
    return label


def generate_event() -> Event:
    detection = random_detection()
    agent_b = random_agent_b_label(detection.label)
    decision = decide(detection.label, detection.confidence, agent_b)

    return Event(
        id=str(uuid.uuid4()),
        ts=time.time(),
        detection=detection,
        decision=Decision(
            route=decision.route,
            contamination_flag=decision.contamination_flag,
            agent_disagreement=decision.agent_disagreement,
            reason=decision.reason,
        ),
    )
