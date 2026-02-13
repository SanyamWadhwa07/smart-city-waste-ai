"""
Unified Inference Pipeline - Dual-Agent Waste Intelligence System.

Orchestrates the complete perception and decision pipeline:
    Camera → Detector → Crops → Classifier → Decision → Routing → Event

Production-grade features:
- Failsafe operation (never crashes)
- Performance tracking
- Structured logging
- Exception handling at each stage
- Compatible with existing Event schema
- WebSocket streaming support
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import List, Iterator, Optional, Dict
import numpy as np
import cv2

from ..detector import WasteDetector, DetectorResult
from ..classifier import MaterialClassifier, ClassifierResult
from ..decision import DecisionEngine, ObjectDecision, RoutingEngine
from ..schemas import Event, Detection, Decision
from ..logging_config import inference_logger, PerformanceTracker
from ..errors import ModelInferenceError, CameraError


@dataclass
class AnalysisResult:
    """Complete analysis result for a frame."""
    
    timestamp: float
    frame_id: str
    objects: List[Dict]  # List of object dictionaries
    total_objects: int
    processing_time_ms: float
    stage_timings: Dict[str, float]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "timestamp": self.timestamp,
            "frame_id": self.frame_id,
            "objects": self.objects,
            "total_objects": self.total_objects,
            "processing_time_ms": self.processing_time_ms,
            "stage_timings": self.stage_timings,
        }


class DualAgentPipeline:
    """
    Production inference pipeline for waste intelligence.
    
    Implements complete flow:
    1. Detection (Stage 1) - Object localization
    2. Classification (Stage 2) - Material identification on crops
    3. Decision - Conflict resolution
    4. Routing - Bin recommendations
    5. Event generation - Backend integration
    """
    
    def __init__(
        self,
        detector: WasteDetector = None,
        classifier: MaterialClassifier = None,
        decision_engine: DecisionEngine = None,
        routing_engine: RoutingEngine = None,
        camera_source: Optional[int] = None,
        encode_frames: bool = True,
        verbose: bool = False
    ):
        """
        Initialize inference pipeline.
        
        Args:
            detector: WasteDetector instance (creates if None)
            classifier: MaterialClassifier instance (creates if None)
            decision_engine: DecisionEngine instance (creates if None)
            routing_engine: RoutingEngine instance (creates if None)
            camera_source: Camera index or video path (None to skip camera init)
            encode_frames: Whether to encode frames in events
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.encode_frames = encode_frames
        
        # Initialize components
        inference_logger.info("Initializing dual-agent pipeline...")
        
        self.detector = detector or WasteDetector(verbose=verbose)
        self.classifier = classifier or MaterialClassifier(verbose=verbose)
        self.decision_engine = decision_engine or DecisionEngine(verbose=verbose)
        self.routing_engine = routing_engine or RoutingEngine(verbose=verbose)
        
        # Performance tracking
        self.perf_tracker = PerformanceTracker(inference_logger)
        
        # Camera (optional)
        self.camera = None
        if camera_source is not None:
            self.camera = self._init_camera(camera_source)
        
        inference_logger.info(
            "Pipeline initialized",
            extra={
                "detector": self.detector.get_info(),
                "classifier": self.classifier.get_info(),
                "camera_enabled": self.camera is not None,
            }
        )
    
    def _init_camera(self, source) -> cv2.VideoCapture:
        """Initialize camera with retry logic."""
        inference_logger.info(f"Initializing camera: {source}")
        
        try:
            cap = cv2.VideoCapture(source)
            
            if not cap.isOpened():
                raise CameraError(f"Failed to open camera: {source}")
            
            # Test read
            ret, frame = cap.read()
            if not ret or frame is None:
                raise CameraError(f"Failed to read from camera: {source}")
            
            inference_logger.info("Camera initialized successfully")
            return cap
            
        except Exception as e:
            inference_logger.error(f"Camera initialization failed: {e}")
            raise CameraError(f"Camera init failed: {e}")
    
    def analyze_frame(
        self,
        frame: np.ndarray,
        frame_id: Optional[str] = None
    ) -> AnalysisResult:
        """
        Analyze a single frame through complete pipeline.
        
        Args:
            frame: Input frame (HxWxC numpy array)
            frame_id: Optional frame identifier
        
        Returns:
            AnalysisResult with complete analysis
        
        Raises:
            ModelInferenceError: If pipeline fails critically
        """
        if frame_id is None:
            frame_id = f"frame_{uuid.uuid4().hex[:8]}"
        
        start_time = time.perf_counter()
        stage_timings = {}
        
        try:
            # Stage 1: Detection
            t0 = time.perf_counter()
            detections, crops = self.detector.detect(frame, return_crops=True)
            stage_timings["detection"] = (time.perf_counter() - t0) * 1000
            
            inference_logger.debug(
                f"Detected {len(detections)} objects",
                extra={"frame_id": frame_id, "count": len(detections)}
            )
            
            # Failsafe: No detections
            if not detections:
                total_time = (time.perf_counter() - start_time) * 1000
                return AnalysisResult(
                    timestamp=time.time(),
                    frame_id=frame_id,
                    objects=[],
                    total_objects=0,
                    processing_time_ms=total_time,
                    stage_timings=stage_timings,
                )
            
            # Stage 2: Classification (only on crops)
            t1 = time.perf_counter()
            classifications = self.classifier.classify_batch(crops, return_top_k=True)
            stage_timings["classification"] = (time.perf_counter() - t1) * 1000
            
            # Stage 3: Decision
            t2 = time.perf_counter()
            decisions = self.decision_engine.batch_decide(detections, classifications)
            stage_timings["decision"] = (time.perf_counter() - t2) * 1000
            
            # Stage 4: Routing
            t3 = time.perf_counter()
            routes = self.routing_engine.batch_route(decisions)
            stage_timings["routing"] = (time.perf_counter() - t3) * 1000
            
            # Build objects list
            objects = []
            for i, (detection, classification, decision, (route, bin_rec)) in enumerate(
                zip(detections, classifications, decisions, routes)
            ):
                obj = {
                    "id": f"obj_{i}",
                    "bbox": detection.bbox,
                    "detector_label": detection.label,
                    "classifier_label": classification.label,
                    "confidence_detector": detection.confidence,
                    "confidence_classifier": classification.confidence,
                    "decision": decision.decision_type,
                    "final_material": decision.final_material,
                    "recommended_bin": bin_rec,
                    "route": route.route,
                    "contamination_flag": route.contamination_flag,
                    "reason": route.reason,
                }
                objects.append(obj)
            
            total_time = (time.perf_counter() - start_time) * 1000
            
            # Track performance
            self.perf_tracker.record_timing("analyze_frame", total_time)
            
            if self.verbose:
                inference_logger.debug(
                    f"Frame analyzed in {total_time:.1f}ms",
                    extra={"frame_id": frame_id, "objects": len(objects)}
                )
            
            return AnalysisResult(
                timestamp=time.time(),
                frame_id=frame_id,
                objects=objects,
                total_objects=len(objects),
                processing_time_ms=total_time,
                stage_timings=stage_timings,
            )
            
        except Exception as e:
            inference_logger.error(f"Pipeline failed for frame {frame_id}: {e}")
            # Return empty result instead of crashing
            return AnalysisResult(
                timestamp=time.time(),
                frame_id=frame_id,
                objects=[],
                total_objects=0,
                processing_time_ms=(time.perf_counter() - start_time) * 1000,
                stage_timings=stage_timings,
            )
    
    def analyze_frame_to_event(
        self,
        frame: np.ndarray,
        event_id: Optional[str] = None
    ) -> Event:
        """
        Analyze frame and convert to Event schema (backend compatibility).
        
        Args:
            frame: Input frame
            event_id: Optional event ID
        
        Returns:
            Event compatible with existing backend/frontend
        """
        if event_id is None:
            event_id = f"evt_{uuid.uuid4().hex[:12]}"
        
        # Run analysis
        result = self.analyze_frame(frame, frame_id=event_id)
        
        # Handle no detections
        if result.total_objects == 0:
            # Return minimal event
            return Event(
                id=event_id,
                ts=result.timestamp,
                detection=Detection(
                    label="NO_DETECTION",
                    confidence=0.0,
                    bbox=[0.0, 0.0, 0.0, 0.0],
                ),
                decision=Decision(
                    route="LANDFILL",
                    contamination_flag=False,
                    agent_disagreement=False,
                    reason="No objects detected",
                ),
                frame=self._encode_frame(frame) if self.encode_frames else None,
            )
        
        # Take first object (multi-object support would need multiple events)
        obj = result.objects[0]
        
        # Create Event schema
        event = Event(
            id=event_id,
            ts=result.timestamp,
            detection=Detection(
                label=obj["detector_label"],
                confidence=obj["confidence_detector"],
                bbox=obj["bbox"],
            ),
            decision=Decision(
                route=obj["route"],
                contamination_flag=obj["contamination_flag"],
                agent_disagreement=(
                    obj["detector_label"] != obj["classifier_label"]
                ),
                reason=obj["reason"],
                contamination_score=obj.get("contamination_score"),
                confidence_score=obj.get("confidence_score"),
                material_agent_decision=obj.get("final_material"),
                routing_agent_decision=obj.get("classifier_label"),
            ),
            frame=self._encode_frame(frame) if self.encode_frames else None,
        )
        
        return event
    
    def stream_events(
        self,
        fps_limit: Optional[float] = 30.0
    ) -> Iterator[Event]:
        """
        Stream events from camera in real-time.
        
        Args:
            fps_limit: Maximum FPS (None for unlimited)
        
        Yields:
            Event objects
        
        Raises:
            CameraError: If camera not initialized or fails
        """
        if self.camera is None:
            raise CameraError("Camera not initialized")
        
        frame_delay = 1.0 / fps_limit if fps_limit else 0.0
        last_frame_time = 0.0
        
        inference_logger.info("Starting event stream...")
        
        try:
            while True:
                # FPS limiting
                current_time = time.time()
                if current_time - last_frame_time < frame_delay:
                    time.sleep(0.001)
                    continue
                
                # Read frame
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    inference_logger.warning("Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
                
                # Analyze and yield event
                try:
                    event = self.analyze_frame_to_event(frame)
                    yield event
                    last_frame_time = time.time()
                except Exception as e:
                    inference_logger.error(f"Frame analysis failed: {e}")
                    # Continue streaming despite error
                    continue
                    
        except KeyboardInterrupt:
            inference_logger.info("Event stream stopped by user")
        finally:
            self._cleanup_camera()
    
    def _encode_frame(self, frame: np.ndarray) -> Optional[str]:
        """Encode frame as base64 JPEG."""
        try:
            import base64
            
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            
            # Convert to base64
            encoded = base64.b64encode(buffer).decode('utf-8')
            return encoded
            
        except Exception as e:
            inference_logger.warning(f"Frame encoding failed: {e}")
            return None
    
    def _cleanup_camera(self):
        """Release camera resources."""
        if self.camera is not None:
            try:
                self.camera.release()
                inference_logger.info("Camera released")
            except Exception as e:
                inference_logger.error(f"Camera cleanup failed: {e}")
    
    def get_performance_stats(self) -> dict:
        """Get pipeline performance statistics."""
        return self.perf_tracker.get_stats()
    
    def get_info(self) -> dict:
        """Get pipeline information."""
        return {
            "detector": self.detector.get_info(),
            "classifier": self.classifier.get_info(),
            "decision_engine": self.decision_engine.get_info(),
            "routing_engine": self.routing_engine.get_info(),
            "camera_enabled": self.camera is not None,
            "encode_frames": self.encode_frames,
        }
    
    def __del__(self):
        """Cleanup on deletion."""
        self._cleanup_camera()
