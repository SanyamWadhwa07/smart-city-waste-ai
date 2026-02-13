from __future__ import annotations

import asyncio
import os
import random
import base64
from io import BytesIO
from typing import Optional
import numpy as np
import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables from .env file FIRST
from dotenv import load_dotenv
load_dotenv()

from .schemas import (
    AlertResponse,
    ContaminationMetricsResponse,
    Event,
    ImpactSummary,
    Metrics,
    ReviewQueueItem,
    ReviewQueueResponse,
    ThresholdSnapshot,
    WindowMetrics,
)
from .simulator import generate_event
from .impact import ImpactTracker
from .adaptive import AdaptiveThresholdManager
from .contamination_monitor import ContaminationMonitor
from .logging_config import api_logger, system_logger
from .utils.warmup import warmup_pipeline

USE_REAL_INFERENCE = os.getenv("USE_REAL_INFERENCE", "0") == "1"

# Try to import new pipeline
_pipeline = None
try:
    from .pipeline import DualAgentPipeline
except ImportError as e:
    DualAgentPipeline = None
    system_logger.warning(f"New pipeline not available: {e}")

app = FastAPI(title="CogniRecycle Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event handler
@app.on_event("startup")
async def startup_event():
    """Initialize pipeline and warmup models."""
    global _pipeline
    
    if not USE_REAL_INFERENCE:
        system_logger.info("Running in simulation mode (USE_REAL_INFERENCE=0)")
        return
    
    if DualAgentPipeline is None:
        system_logger.warning("New pipeline not available, will use legacy or simulation")
        return
    
    try:
        system_logger.info("Initializing production pipeline...")
        
        # Initialize pipeline (without camera, will be created per-websocket)
        _pipeline = DualAgentPipeline(
            camera_source=None,  # Camera initialized in WebSocket
            encode_frames=True,
            verbose=False
        )
        
        system_logger.info("Pipeline components initialized")
        system_logger.info(f"Pipeline info: {_pipeline.get_info()}")
        
        # Warmup models
        system_logger.info("Starting model warmup...")
        warmup_stats = warmup_pipeline(_pipeline, num_frames=10, verbose=True)
        system_logger.info(f"Warmup complete: {warmup_stats}")
        
        system_logger.info("✓ Production pipeline ready")
        
    except Exception as e:
        system_logger.error(f"Pipeline initialization failed: {e}")
        system_logger.warning("Falling back to simulation mode")
        _pipeline = None


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources."""
    global _pipeline
    if _pipeline is not None:
        try:
            system_logger.info("Shutting down pipeline...")
            del _pipeline
            _pipeline = None
        except Exception as e:
            system_logger.error(f"Pipeline shutdown error: {e}")

_state = {
    "items_processed": 0,
    "contamination_alerts": 0,
    "system_accuracy": 0.95,
    "efficiency_score": 0.82,
    "co2_saved_kg": 0.0,
    "recovery_value_usd": 0.0,
    "successful_detections": 0,
    "high_confidence_count": 0,
}

impact_tracker = ImpactTracker()
adaptive_manager = AdaptiveThresholdManager()
contamination_monitor = ContaminationMonitor()

# Manual review queue (in-memory for MVP)
review_queue: list[ReviewQueueItem] = []
MAX_QUEUE_SIZE = 100  # Keep last 100 items

def update_metrics(event: Event) -> None:
    _state["items_processed"] += 1
    if event.decision.contamination_flag:
        _state["contamination_alerts"] += 1

    # Track successful detections (high confidence or successful classification)
    if event.detection.confidence >= 0.5:  # Successful detection threshold
        _state["successful_detections"] += 1
    
    # Track high confidence detections for efficiency calculation
    if event.detection.confidence >= 0.75:
        _state["high_confidence_count"] += 1

    # Add to review queue if flagged for manual review
    if event.decision.route == "MANUAL_REVIEW" or event.decision.agent_disagreement:
        review_item = ReviewQueueItem(
            event_id=event.id,
            timestamp=str(event.ts),
            detection=event.detection,
            decision=event.decision,
            reason=event.decision.reason or "Low confidence or agent disagreement",
            status="pending",
        )
        review_queue.append(review_item)
        # Keep queue size limited
        if len(review_queue) > MAX_QUEUE_SIZE:
            review_queue.pop(0)

    # Environmental & economic impact
    impact_tracker.record_event(
        object_class=event.detection.label,
        routing_decision=event.decision.route,
        contaminated=event.decision.contamination_flag,
        agent_disagreement=event.decision.agent_disagreement,
    )
    snap = impact_tracker.summary()
    _state["co2_saved_kg"] = snap.total_co2_kg
    _state["recovery_value_usd"] = snap.revenue_usd

    # Adaptive learning tracking
    adaptive_manager.record_event(
        material_type=event.detection.label,
        contamination_flag=event.decision.contamination_flag,
        agent_disagreement=event.decision.agent_disagreement,
        confidence=event.detection.confidence,
    )

    # Contamination monitor for rolling analytics + alerts
    contamination_monitor.record(event)

    # Calculate real system accuracy based on successful detections
    if _state["items_processed"] > 0:
        _state["system_accuracy"] = round(_state["successful_detections"] / _state["items_processed"], 2)
    
    # Calculate efficiency based on high confidence rate and low contamination
    if _state["items_processed"] > 0:
        confidence_ratio = _state["high_confidence_count"] / _state["items_processed"]
        contamination_ratio = 1 - (_state["contamination_alerts"] / _state["items_processed"])
        _state["efficiency_score"] = round((confidence_ratio * 0.6 + contamination_ratio * 0.4), 2)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "inference_mode": "real" if USE_REAL_INFERENCE else "simulation",
        "pipeline_ready": _pipeline is not None,
        "use_real_inference_env": os.getenv("USE_REAL_INFERENCE", "NOT_SET"),
        "use_real_inference_var": USE_REAL_INFERENCE,
    }


# ============================================================================
# NEW REST API ENDPOINT - Frame Analysis
# ============================================================================

class AnalyzeFrameResponse(BaseModel):
    """Response model for frame analysis."""
    timestamp: str
    frame_id: str
    objects: list[dict]
    total_objects: int
    processing_time_ms: float
    stage_timings: Optional[dict] = None


@app.post("/analyze-frame", response_model=AnalyzeFrameResponse)
async def analyze_frame(
    file: UploadFile = File(...),
    include_timings: bool = False
):
    """
    Analyze a single image frame.
    
    Upload an image file and receive object detection, classification,
    and routing recommendations.
    
    Args:
        file: Image file (JPEG, PNG, etc.)
        include_timings: Include per-stage timing breakdown
    
    Returns:
        Analysis result with detected objects and routing recommendations
    
    Example Response:
        {
            "timestamp": "2026-02-13T12:34:56",
            "frame_id": "frame_abc123",
            "objects": [
                {
                    "id": "obj_0",
                    "bbox": [0.1, 0.2, 0.3, 0.4],
                    "detector_label": "bottle",
                    "classifier_label": "plastic",
                    "confidence_detector": 0.87,
                    "confidence_classifier": 0.92,
                    "decision": "HIGH_CONFIDENCE",
                    "final_material": "plastic",
                    "recommended_bin": "BLUE_BIN",
                    "route": "PLASTIC_BIN"
                }
            ],
            "total_objects": 1,
            "processing_time_ms": 145.3
        }
    """
    if _pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Inference pipeline not available. Check server logs."
        )
    
    try:
        # Read uploaded file
        contents = await file.read()
        
        # Decode image
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file. Supported formats: JPEG, PNG"
            )
        
        # Analyze frame
        result = _pipeline.analyze_frame(frame)
        
        # Build response
        from datetime import datetime
        response = AnalyzeFrameResponse(
            timestamp=datetime.fromtimestamp(result.timestamp).isoformat(),
            frame_id=result.frame_id,
            objects=result.objects,
            total_objects=result.total_objects,
            processing_time_ms=round(result.processing_time_ms, 2),
            stage_timings=result.stage_timings if include_timings else None,
        )
        
        api_logger.info(
            f"Frame analyzed: {result.total_objects} objects, {result.processing_time_ms:.1f}ms"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Frame analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Frame analysis failed: {str(e)}"
        )


# ============================================================================
# Existing Endpoints
# ============================================================================

@app.get("/metrics", response_model=Metrics)
async def metrics():
    return Metrics(**_state)


@app.get("/impact/summary", response_model=ImpactSummary)
async def impact_summary():
    snap = impact_tracker.summary()
    history = [
        {"ts": ts, "co2_saved": co2, "revenue": rev} for ts, co2, rev in snap.history
    ]
    return ImpactSummary(
        total_co2_kg=snap.total_co2_kg,
        revenue_usd=snap.revenue_usd,
        contamination_prevented=snap.contamination_prevented,
        by_material_co2=snap.by_material_co2,
        history=history,
        last_updated=snap.last_updated.isoformat(),
    )


@app.get("/learning/thresholds", response_model=ThresholdSnapshot)
async def learning_snapshot():
    return adaptive_manager.snapshot()


@app.get("/contamination/metrics", response_model=ContaminationMetricsResponse)
async def contamination_metrics():
    payload = contamination_monitor.metrics_payload()
    return ContaminationMetricsResponse(
        short_term=WindowMetrics(**payload["short_term"]),
        medium_term=WindowMetrics(**payload["medium_term"]),
        long_term=WindowMetrics(**payload["long_term"]),
    )


@app.get("/contamination/alerts", response_model=list[AlertResponse])
async def contamination_alerts():
    alerts = contamination_monitor.generate_alerts()
    return [AlertResponse(**a) for a in alerts]


@app.get("/review/queue", response_model=ReviewQueueResponse)
async def get_review_queue():
    """Get items flagged for manual review."""
    pending = sum(1 for item in review_queue if item.status == "pending")
    reviewed = len(review_queue) - pending
    return ReviewQueueResponse(
        items=review_queue,
        total=len(review_queue),
        pending=pending,
        reviewed=reviewed,
    )


@app.post("/review/queue/{event_id}")
async def update_review_item(event_id: str, status: str, reviewed_by: str | None = None):
    """Update review status for an item."""
    from datetime import datetime
    
    for item in review_queue:
        if item.event_id == event_id:
            item.status = status
            item.reviewed_by = reviewed_by
            item.reviewed_at = datetime.now().isoformat()
            return {"success": True, "event_id": event_id, "status": status}
    
    return {"success": False, "error": "Item not found"}


@app.websocket("/ws/video-analysis")
async def video_analysis_stream(ws: WebSocket):
    """
    WebSocket endpoint for video file or camera analysis streaming.
    
    Client sends: {"action": "start", "source": "path/to/video.mp4" or 0 for camera}
    Server sends: Detection events, logs, and metadata
    """
    await ws.accept()
    api_logger.info("Video analysis WebSocket connected")
    
    try:
        # Wait for start command from client
        data = await ws.receive_json()
        action = data.get("action")
        
        if action == "start":
            source = data.get("source", 0)  # Default to camera 0
            max_fps = data.get("max_fps", 5)  # Default to 5 FPS for bandwidth
            
            if _pipeline is None:
                await ws.send_json({
                    "type": "error",
                    "message": "Pipeline not initialized"
                })
                return
            
            from .video_stream import VideoAnalysisStreamer
            streamer = VideoAnalysisStreamer(_pipeline, update_metrics_callback=update_metrics)
            
            api_logger.info(f"Starting video analysis stream from source: {source}")
            await streamer.stream_video_analysis(ws, source, max_fps)
            
    except WebSocketDisconnect:
        api_logger.info("Video analysis WebSocket disconnected")
    except Exception as e:
        api_logger.error(f"Video analysis WebSocket error: {e}")
        try:
            await ws.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass


@app.websocket("/ws/detections")
async def detections(ws: WebSocket):
    """
    WebSocket endpoint for real-time detection stream.
    
    Streams Event objects compatible with existing frontend dashboard.
    """
    await ws.accept()
    
    try:
        # Use new pipeline if available
        if USE_REAL_INFERENCE and _pipeline is not None:
            api_logger.info("WebSocket: Using production pipeline")
            
            # Initialize camera for this connection
            camera_source = int(os.getenv("CAMERA_SOURCE", "0"))
            
            try:
                # Create dedicated pipeline instance with camera
                stream_pipeline = DualAgentPipeline(
                    detector=_pipeline.detector,  # Reuse loaded models
                    classifier=_pipeline.classifier,
                    decision_engine=_pipeline.decision_engine,
                    routing_engine=_pipeline.routing_engine,
                    camera_source=camera_source,
                    encode_frames=True,
                    verbose=False
                )
                
                # Stream events
                for event in stream_pipeline.stream_events(fps_limit=30.0):
                    update_metrics(event)
                    await ws.send_json(event.model_dump())
                    await asyncio.sleep(0.02)
                    
            except Exception as e:
                api_logger.error(f"Pipeline streaming failed: {e}")
                await ws.close(code=1011, reason=f"Pipeline error: {str(e)}")
                
        # Simulation mode
        else:
            api_logger.info("WebSocket: Using simulation mode")
            while True:
                event = generate_event()
                update_metrics(event)
                await ws.send_json(event.model_dump())
                await asyncio.sleep(random.uniform(0.8, 1.6))
                
    except WebSocketDisconnect:
        api_logger.info("WebSocket disconnected")
        return
    except Exception as e:
        api_logger.error(f"WebSocket error: {e}")
        raise
