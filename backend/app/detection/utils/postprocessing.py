from __future__ import annotations

"""Post-processing helpers: NMS and coordinate conversion."""

from typing import List, Tuple

import numpy as np


def xywh_to_xyxy(box: np.ndarray) -> np.ndarray:
    x, y, w, h = box
    return np.array([x - w / 2, y - h / 2, x + w / 2, y + h / 2])


def denormalize_bbox(xyxy: np.ndarray, scale: float, offset: Tuple[int, int]) -> List[float]:
    left, top = offset
    x1, y1, x2, y2 = xyxy
    x1 = (x1 - left) / scale
    y1 = (y1 - top) / scale
    x2 = (x2 - left) / scale
    y2 = (y2 - top) / scale
    return [round(v, 3) for v in [x1, y1, x2 - x1, y2 - y1]]


def nms(boxes: np.ndarray, scores: np.ndarray, iou_threshold: float = 0.45) -> List[int]:
    """Simple NMS implementation."""
    idxs = scores.argsort()[::-1]
    keep: List[int] = []
    while idxs.size > 0:
        i = idxs[0]
        keep.append(i)
        if idxs.size == 1:
            break
        ious = _iou(boxes[i], boxes[idxs[1:]])
        idxs = idxs[1:][ious < iou_threshold]
    return keep


def _iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])
    inter = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    area_a = (box[2] - box[0]) * (box[3] - box[1])
    area_b = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    return inter / (area_a + area_b - inter + 1e-6)
