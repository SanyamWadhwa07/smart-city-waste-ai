from __future__ import annotations

import os
import time
from dataclasses import dataclass

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    from ultralytics import YOLO  # type: ignore
except Exception as exc:  # pragma: no cover - optional dependency
    raise RuntimeError(
        "YOLO inference dependencies not installed. "
        "Install requirements-yolo.txt to enable real inference."
    ) from exc

from .decision import decide
from .schemas import Detection, Decision, Event


@dataclass
class InferenceConfig:
    model_path: str
    device: str = "cpu"
    conf: float = 0.35
    imgsz: int = 640
    source: str = "0"


class YoloInference:
    def __init__(self, config: InferenceConfig) -> None:
        self.config = config
        self.model = YOLO(config.model_path)
        self.cap = cv2.VideoCapture(int(config.source) if config.source.isdigit() else config.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera/source: {config.source}")

    def _normalize_bbox(self, xyxy: list[float], w: int, h: int) -> list[float]:
        x1, y1, x2, y2 = xyxy
        x = max(0.0, min(1.0, x1 / w))
        y = max(0.0, min(1.0, y1 / h))
        bw = max(0.0, min(1.0, (x2 - x1) / w))
        bh = max(0.0, min(1.0, (y2 - y1) / h))
        return [round(x, 3), round(y, 3), round(bw, 3), round(bh, 3)]

    def next_event(self) -> Event | None:
        ok, frame = self.cap.read()
        if not ok or frame is None:
            return None

        h, w = frame.shape[:2]
        results = self.model.predict(
            source=frame,
            conf=self.config.conf,
            imgsz=self.config.imgsz,
            device=self.config.device,
            verbose=False,
        )

        if not results or results[0].boxes is None or len(results[0].boxes) == 0:
            return None

        boxes = results[0].boxes
        box = boxes[0]
        cls_id = int(box.cls[0].item()) if hasattr(box.cls[0], "item") else int(box.cls[0])
        label = self.model.names.get(cls_id, str(cls_id))
        confidence = float(box.conf[0].item()) if hasattr(box.conf[0], "item") else float(box.conf[0])
        xyxy = box.xyxy[0].tolist() if hasattr(box.xyxy[0], "tolist") else list(box.xyxy[0])

        detection = Detection(
            label=label,
            confidence=round(confidence, 2),
            bbox=self._normalize_bbox(xyxy, w, h),
        )

        decision_result = decide(detection.label, detection.confidence, None)
        return Event(
            id=str(int(time.time() * 1000)),
            ts=time.time(),
            detection=detection,
            decision=Decision(
                route=decision_result.route,
                contamination_flag=decision_result.contamination_flag,
                agent_disagreement=decision_result.agent_disagreement,
                reason=decision_result.reason,
                contamination_score=decision_result.contamination_score,
                confidence_score=decision_result.confidence_score,
                material_agent_decision=decision_result.material_agent_decision,
                routing_agent_decision=decision_result.routing_agent_decision,
            ),
        )

    def close(self) -> None:
        self.cap.release()


def load_inference_from_env() -> YoloInference:
    config = InferenceConfig(
        model_path=os.getenv("MODEL_PATH", "models/yolov8n.pt"),
        device=os.getenv("MODEL_DEVICE", "cpu"),
        conf=float(os.getenv("MODEL_CONF", "0.35")),
        imgsz=int(os.getenv("MODEL_IMGSZ", "640")),
        source=os.getenv("CAMERA_SOURCE", "0"),
    )
    return YoloInference(config)
