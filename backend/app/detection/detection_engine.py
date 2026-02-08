from __future__ import annotations

"""Real-time waste detection engine (feature 1)."""

import time
from typing import Callable, Iterable, List, Optional, Tuple
import random

import numpy as np

from .config import DetectionConfig
from .utils.preprocessing import letterbox_resize, normalize
from .utils.postprocessing import denormalize_bbox, nms, xywh_to_xyxy


class WasteDetectionEngine:
    """
    Lightweight wrapper around YOLOv8 (ONNX) with graceful fallback to simulation
    when hardware/runtime isn't available.
    """

    def __init__(self, config: DetectionConfig | None = None):
        self.config = config or DetectionConfig()
        self.session = None
        self.class_names: List[str] = []
        self._load_model()

    def _load_model(self) -> None:
        try:
            import onnxruntime as ort  # type: ignore
            import yaml  # type: ignore

            self.session = ort.InferenceSession(self.config.model_path, providers=["CPUExecutionProvider"])
            with open(self.config.class_map_path, "r", encoding="utf-8") as f:
                mapping = yaml.safe_load(f) or {}
                # expect mapping like {0: "plastic_bottle", 1: "glass_bottle", ...}
                self.class_names = [v for _, v in sorted(mapping.items(), key=lambda kv: int(kv[0]))]
        except Exception:
            # Fallback: stay in simulated mode
            self.session = None

    def detect_frame(self, frame: np.ndarray) -> List[dict]:
        """
        Run detection on a single frame.
        Returns list of dicts with keys: label, confidence, bbox [x,y,w,h] normalized.
        """
        if frame is None:
            return []
        if self.session is None:
            return self._simulate(frame)

        resized, scale, offset = letterbox_resize(frame, self.config.input_size)
        tensor = normalize(resized).transpose(2, 0, 1)  # CHW
        tensor = np.expand_dims(tensor, 0)

        outputs = self.session.run(None, {self.session.get_inputs()[0].name: tensor})
        preds = outputs[0][0]  # (num, 6) -> x,y,w,h,conf,cls

        boxes_xyxy = np.array([xywh_to_xyxy(p[:4]) for p in preds])
        scores = preds[:, 4]
        classes = preds[:, 5].astype(int)

        keep = nms(boxes_xyxy, scores, self.config.nms_threshold)
        detections = []
        for idx in keep:
            conf = float(scores[idx])
            if conf < self.config.confidence_threshold:
                continue
            bbox = denormalize_bbox(boxes_xyxy[idx], scale, offset)
            cls_id = classes[idx]
            label = self.class_names[cls_id] if cls_id < len(self.class_names) else str(cls_id)
            detections.append({"label": label, "confidence": round(conf, 2), "bbox": bbox})
        return detections

    def _simulate(self, frame: np.ndarray) -> List[dict]:
        """Fallback simulation to keep pipeline running without model/hardware."""
        h, w = frame.shape[:2]
        labels = [
            "plastic_bottle",
            "glass_bottle",
            "aluminum_can",
            "cardboard",
            "food_scrap",
            "battery",
            "plastic_bag",
            "paper",
        ]
        bbox = [
            round(random.uniform(0.05, 0.6), 2),
            round(random.uniform(0.05, 0.6), 2),
            round(random.uniform(0.1, 0.3), 2),
            round(random.uniform(0.1, 0.3), 2),
        ]
        return [
            {
                "label": random.choice(labels),
                "confidence": round(random.uniform(0.7, 0.98), 2),
                "bbox": bbox,
            }
        ]

    def process_video_stream(self, capture_fn: Callable[[], Optional[np.ndarray]], callback: Callable[[dict], None]):
        """
        Continuously capture frames from `capture_fn` and send detections to `callback`.
        """
        while True:
            frame = capture_fn()
            if frame is None:
                time.sleep(0.05)
                continue
            for det in self.detect_frame(frame):
                callback(det)
            time.sleep(0.02)
