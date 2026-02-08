from __future__ import annotations

"""Lightweight preprocessing helpers for YOLO-style models."""

from typing import Tuple

import numpy as np


def letterbox_resize(image: np.ndarray, target_size: Tuple[int, int]) -> Tuple[np.ndarray, float, Tuple[int, int]]:
    """Resize with unchanged aspect ratio using padding."""
    h, w = image.shape[:2]
    target_w, target_h = target_size
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2_resize(image, (new_w, new_h))
    padded = np.full((target_h, target_w, 3), 114, dtype=np.uint8)

    top = (target_h - new_h) // 2
    left = (target_w - new_w) // 2
    padded[top : top + new_h, left : left + new_w] = resized
    return padded, scale, (left, top)


def normalize(image: np.ndarray) -> np.ndarray:
    """Normalize to 0-1 float tensor."""
    return image.astype(np.float32) / 255.0


def cv2_resize(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    """Local wrapper to avoid hard dependency when OpenCV missing."""
    try:
        import cv2  # type: ignore

        return cv2.resize(image, size)
    except Exception:
        # Fallback using PIL if OpenCV not installed
        from PIL import Image

        pil = Image.fromarray(image)
        return np.array(pil.resize(size))
