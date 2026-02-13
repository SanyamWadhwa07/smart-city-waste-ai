"""
Waste Detector Agent - Stage 1 of Dual-Agent Pipeline.

Uses turhancan97/yolov8-segment-trash-detection for object detection and segmentation.
Detects waste items (Glass, Metal, Paper, Plastic, Waste) and extracts bounding boxes + crops.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path
import numpy as np
import cv2

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    hf_hub_download = None

from ..utils.gpu import get_device, enable_fp16, optimize_memory
from ..logging_config import inference_logger
from ..errors import ModelInferenceError


@dataclass
class DetectorResult:
    """Result from detector for a single object."""
    
    label: str
    confidence: float
    bbox: List[float]  # [x, y, w, h] normalized to [0, 1]
    bbox_abs: List[int]  # [x, y, w, h] absolute pixels
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "label": self.label,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "bbox_abs": self.bbox_abs,
        }


class WasteDetector:
    """
    Waste object detector using YOLOv8.
    
    Loads pretrained BowerApp trash detection model and runs inference
    on frames to detect waste objects with bounding boxes.
    
    Features:
    - GPU acceleration with FP16 support
    - Configurable confidence threshold
    - NMS (Non-Maximum Suppression) 
    - Normalized bbox output [0, 1]
    - Crop extraction for Stage 2 classification
    """
    
    def __init__(
        self,
        model_path: str = None,
        confidence_threshold: float = 0.40,
        iou_threshold: float = 0.45,
        image_size: int = 640,
        device: str = None,
        half: bool = None,
        verbose: bool = False
    ):
        """
        Initialize waste detector.
        
        Args:
            model_path: Path to YOLO model file or HuggingFace repo
            confidence_threshold: Minimum confidence for detections
            iou_threshold: IoU threshold for NMS
            image_size: Input image size for model
            device: Device to use ("cpu", "cuda", or None for auto)
            half: Enable FP16 (None for auto-detect)
            verbose: Enable verbose logging
        """
        if YOLO is None:
            raise ImportError(
                "ultralytics not installed. Install with: pip install ultralytics"
            )
        
        # Configuration
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.image_size = image_size
        self.verbose = verbose
        
        # Device setup
        self.device = get_device(device)
        self.half = enable_fp16(self.device) if half is None else half
        
        # Model path
        if model_path is None:
            model_path = os.getenv(
                "TIER1_MODEL_PATH",
                "models/yolov8m-seg.pt"
            )
        self.model_path = model_path
        
        # Load model
        inference_logger.info(
            "Loading detector",
            extra={
                "model_path": model_path,
                "device": self.device,
                "fp16": self.half,
                "conf_threshold": confidence_threshold,
            }
        )
        
        try:
            self.model = self._load_model()
            inference_logger.info("Detector loaded successfully")
        except Exception as e:
            inference_logger.error(f"Failed to load detector: {e}")
            raise ModelInferenceError(f"Detector loading failed: {e}")
        
        # Apply optimizations
        optimize_memory(self.device)
    
    def _load_model(self) -> YOLO:
        """Load YOLO model with proper configuration."""
        try:
            model_path = self.model_path
            
            # Check if path exists or is relative
            if not os.path.isabs(model_path):
                # Try relative to backend/app/detector
                base_paths = [
                    Path(__file__).parent.parent.parent / model_path,  # From backend/
                    Path(model_path),  # Current directory
                ]
                
                for base_path in base_paths:
                    if base_path.exists():
                        model_path = str(base_path)
                        break
                else:
                    inference_logger.warning(f"Model not found at {model_path}, trying as-is")
            
            inference_logger.info(f"Loading model from: {model_path}")
            
            # Load model (supports both detection and segmentation)
            model = YOLO(model_path)
            
            # Configure device
            model.to(self.device)
            
            # Enable FP16 if requested
            if self.half and self.device == "cuda":
                try:
                    model.model.half()
                except Exception as e:
                    inference_logger.warning(f"Could not enable FP16: {e}")
                    self.half = False
            
            return model
            
        except Exception as e:
            raise ModelInferenceError(f"Failed to load YOLO model: {e}")
    
    def detect(
        self,
        frame: np.ndarray,
        return_crops: bool = False
    ) -> Tuple[List[DetectorResult], Optional[List[np.ndarray]]]:
        """
        Run detection on a single frame.
        
        Args:
            frame: Input frame (HxWxC numpy array, BGR or RGB)
            return_crops: Whether to extract and return crops
        
        Returns:
            Tuple of (detections, crops)
            - detections: List of DetectorResult objects
            - crops: List of cropped images (if return_crops=True) or None
        
        Raises:
            ModelInferenceError: If detection fails
        """
        if frame is None or frame.size == 0:
            return [], None
        
        try:
            # Run inference
            results = self.model.predict(
                frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                imgsz=self.image_size,
                half=self.half,
                verbose=self.verbose,
                device=self.device,
            )
            
            # Parse results
            detections = []
            crops = [] if return_crops else None
            
            if len(results) == 0 or results[0].boxes is None:
                return detections, crops
            
            result = results[0]  # Single image inference
            boxes = result.boxes
            
            # Get frame dimensions for normalization
            frame_h, frame_w = frame.shape[:2]
            
            for i in range(len(boxes)):
                # Get box data
                box = boxes.xyxy[i].cpu().numpy()  # [x1, y1, x2, y2]
                conf = float(boxes.conf[i].cpu().numpy())
                cls_id = int(boxes.cls[i].cpu().numpy())
                
                # Get label name
                label = result.names[cls_id] if result.names else f"class_{cls_id}"
                
                # Convert to [x, y, w, h] format
                x1, y1, x2, y2 = box
                x = x1
                y = y1
                w = x2 - x1
                h = y2 - y1
                
                # Absolute coordinates
                bbox_abs = [int(x), int(y), int(w), int(h)]
                
                # Normalized coordinates [0, 1]
                bbox_norm = [
                    x / frame_w,
                    y / frame_h,
                    w / frame_w,
                    h / frame_h
                ]
                
                # Clip to valid range
                bbox_norm = [max(0.0, min(1.0, coord)) for coord in bbox_norm]
                
                detection = DetectorResult(
                    label=label,
                    confidence=conf,
                    bbox=bbox_norm,
                    bbox_abs=bbox_abs
                )
                detections.append(detection)
                
                # Extract crop if requested
                if return_crops:
                    crop = self._extract_crop(frame, bbox_abs)
                    crops.append(crop)
            
            return detections, crops
            
        except Exception as e:
            inference_logger.error(f"Detection failed: {e}")
            raise ModelInferenceError(f"Detector inference failed: {e}")
    
    def _extract_crop(
        self,
        frame: np.ndarray,
        bbox_abs: List[int]
    ) -> np.ndarray:
        """
        Extract crop from frame using absolute bounding box.
        
        Args:
            frame: Input frame
            bbox_abs: Absolute bbox [x, y, w, h]
        
        Returns:
            Cropped image region
        """
        x, y, w, h = bbox_abs
        
        # Ensure coordinates are within frame bounds
        frame_h, frame_w = frame.shape[:2]
        x = max(0, min(x, frame_w - 1))
        y = max(0, min(y, frame_h - 1))
        w = max(1, min(w, frame_w - x))
        h = max(1, min(h, frame_h - y))
        
        # Extract crop
        crop = frame[y:y+h, x:x+w].copy()
        
        return crop
    
    def get_crops(
        self,
        frame: np.ndarray,
        detections: List[DetectorResult]
    ) -> List[np.ndarray]:
        """
        Extract crops for all detections.
        
        Args:
            frame: Input frame
            detections: List of detections
        
        Returns:
            List of cropped images
        """
        crops = []
        for det in detections:
            crop = self._extract_crop(frame, det.bbox_abs)
            crops.append(crop)
        return crops
    
    def visualize(
        self,
        frame: np.ndarray,
        detections: List[DetectorResult],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw bounding boxes on frame for visualization.
        
        Args:
            frame: Input frame
            detections: List of detections
            color: Box color (B, G, R)
            thickness: Line thickness
        
        Returns:
            Frame with boxes drawn
        """
        vis_frame = frame.copy()
        
        for det in detections:
            x, y, w, h = det.bbox_abs
            
            # Draw box
            cv2.rectangle(
                vis_frame,
                (x, y),
                (x + w, y + h),
                color,
                thickness
            )
            
            # Draw label
            label_text = f"{det.label} {det.confidence:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1
            
            (text_w, text_h), _ = cv2.getTextSize(
                label_text, font, font_scale, font_thickness
            )
            
            # Background for text
            cv2.rectangle(
                vis_frame,
                (x, y - text_h - 5),
                (x + text_w, y),
                color,
                -1
            )
            
            # Text
            cv2.putText(
                vis_frame,
                label_text,
                (x, y - 2),
                font,
                font_scale,
                (0, 0, 0),
                font_thickness
            )
        
        return vis_frame
    
    def get_info(self) -> dict:
        """Get detector information for logging."""
        return {
            "model_path": self.model_path,
            "device": self.device,
            "fp16": self.half,
            "confidence_threshold": self.confidence_threshold,
            "iou_threshold": self.iou_threshold,
            "image_size": self.image_size,
        }
