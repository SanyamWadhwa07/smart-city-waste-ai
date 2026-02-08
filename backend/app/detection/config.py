from __future__ import annotations

"""Configuration objects for the real-time detection engine."""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class DetectionConfig:
    model_path: str = "models/yolov8m_waste.onnx"
    class_map_path: str = "models/class_mapping.yaml"
    input_size: Tuple[int, int] = (640, 640)
    confidence_threshold: float = 0.75
    nms_threshold: float = 0.45
    source: str = "0"  # 0 = default webcam, RTSP/url/file supported
