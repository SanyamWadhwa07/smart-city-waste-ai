"""
Real-time video streaming endpoint for dashboard integration.
Processes video and streams detections via WebSocket.
"""
import asyncio
import os
import time
from typing import Optional
import cv2
import numpy as np
from fastapi import WebSocket

from .pipeline import DualAgentPipeline
from .logging_config import api_logger
from .schemas import Event, Detection, Decision


class VideoAnalysisStreamer:
    """Stream video analysis results to frontend via WebSocket."""
    
    def __init__(self, pipeline: DualAgentPipeline, update_metrics_callback=None):
        self.pipeline = pipeline
        self.active_streams = 0
        self.update_metrics_callback = update_metrics_callback
        
    async def stream_video_analysis(
        self,
        websocket: WebSocket,
        video_source: str | int = 0,
        max_fps: int = 10
    ):
        """
        Stream video analysis results to WebSocket client.
        
        Args:
            websocket: WebSocket connection
            video_source: Video file path or camera ID
            max_fps: Maximum frames per second to process
        """
        cap = None
        frame_interval = 1.0 / max_fps
        frame_count = 0
        
        try:
            # Open video source
            if isinstance(video_source, str):
                # Handle relative paths - search in multiple locations
                import os
                from pathlib import Path
                
                if not os.path.isabs(video_source):
                    # Try multiple potential locations
                    search_paths = [
                        Path(video_source),  # Current directory
                        Path.cwd() / video_source,  # Explicit current directory
                        Path(__file__).parent.parent.parent / video_source,  # Project root
                        Path(__file__).parent.parent / video_source,  # Backend directory
                    ]
                    
                    video_path = None
                    for path in search_paths:
                        if path.exists() and path.is_file():
                            video_path = str(path.absolute())
                            break
                    
                    if video_path is None:
                        error_msg = f"Video file not found: {video_source}. Searched in: {', '.join(str(p) for p in search_paths)}"
                        api_logger.error(error_msg)
                        await websocket.send_json({
                            "type": "error",
                            "message": error_msg
                        })
                        return
                    
                    video_source = video_path
                
                cap = cv2.VideoCapture(video_source)
                api_logger.info(f"Opened video file: {video_source}")
            else:
                cap = cv2.VideoCapture(video_source)
                api_logger.info(f"Opened camera: {video_source}")
            
            if not cap.isOpened():
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to open video source"
                })
                return
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Send video metadata
            await websocket.send_json({
                "type": "metadata",
                "fps": float(fps) if fps > 0 else None,
                "width": int(width),
                "height": int(height),
                "total_frames": int(total_frames) if total_frames > 0 else None,
                "is_camera": isinstance(video_source, int)
            })
            
            frame_count = 0
            last_process_time = 0
            
            while True:
                current_time = time.time()
                
                # Throttle frame rate
                if current_time - last_process_time < frame_interval:
                    await asyncio.sleep(0.01)
                    continue
                
                ret, frame = cap.read()
                if not ret:
                    # Video ended
                    await websocket.send_json({
                        "type": "complete",
                        "total_frames": frame_count,
                        "message": "Video analysis complete"
                    })
                    break
                
                frame_count += 1
                last_process_time = current_time
                
                try:
                    # Run pipeline analysis
                    analysis_start = time.time()
                    result = self.pipeline.analyze_frame(frame, frame_id=f"frame_{frame_count}")
                    analysis_time = (time.time() - analysis_start) * 1000
                    
                    # Convert frame to JPEG for streaming
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    frame_base64 = buffer.tobytes().hex()
                    
                    # Build detection data and update metrics
                    detections = []
                    for obj in result.objects:
                        # Convert all numpy types to Python native types for JSON serialization
                        detections.append({
                            "id": str(obj["id"]),
                            "detector_label": str(obj["detector_label"]),
                            "classifier_label": str(obj["classifier_label"]),
                            "confidence_detector": float(obj["confidence_detector"]),
                            "confidence_classifier": float(obj["confidence_classifier"]),
                            "final_material": str(obj["final_material"]),
                            "recommended_bin": str(obj["recommended_bin"]),
                            "bbox": [float(x) for x in obj["bbox"]],
                            "decision": str(obj["decision"]),
                            "contamination_flag": bool(obj["contamination_flag"]),
                            "reason": str(obj["reason"]) if obj["reason"] else None
                        })
                        
                        # Update metrics for each detected object
                        if self.update_metrics_callback:
                            # Create Event object for metrics tracking
                            event = Event(
                                id=f"{result.frame_id}_{obj['id']}",
                                ts=float(result.timestamp),  # Use float timestamp directly
                                detection=Detection(
                                    label=str(obj["final_material"]),
                                    confidence=float(obj["confidence_classifier"]),
                                    bbox=[float(x) for x in obj["bbox"]]
                                ),
                                decision=Decision(
                                    route=str(obj["recommended_bin"]),
                                    contamination_flag=bool(obj["contamination_flag"]),
                                    agent_disagreement=(str(obj["decision"]) == "AGENT_DISAGREEMENT"),
                                    reason=str(obj["reason"]) if obj["reason"] else None
                                )
                            )
                            self.update_metrics_callback(event)
                    
                    # Send detection event
                    await websocket.send_json({
                        "type": "detection",
                        "frame_number": int(frame_count),
                        "timestamp": float(result.timestamp),
                        "frame_id": str(result.frame_id),
                        "detections": detections,
                        "total_objects": int(result.total_objects),
                        "processing_time_ms": float(round(analysis_time, 2)),
                        "frame_data": frame_base64[:1000] if len(frame_base64) < 50000 else None  # Only send small frames
                    })
                    
                    # Also send a log event for terminal-like display
                    log_messages = []
                    if detections:
                        log_messages.append(f"[Frame {frame_count}] Detected {len(detections)} object(s)")
                        for i, det in enumerate(detections, 1):
                            log_messages.append(
                                f"  Object {i}: {det['detector_label']} "
                                f"(det:{det['confidence_detector']:.2f}, cls:{det['confidence_classifier']:.2f}) "
                                f"→ {det['recommended_bin']}"
                            )
                    else:
                        log_messages.append(f"[Frame {frame_count}] No objects detected")
                    
                    await websocket.send_json({
                        "type": "log",
                        "messages": log_messages
                    })
                    
                except Exception as e:
                    api_logger.error(f"Frame analysis error: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Frame {frame_count} analysis failed: {str(e)}"
                    })
                
                # Small delay to prevent overwhelming the connection
                await asyncio.sleep(0.01)
                
        except Exception as e:
            api_logger.error(f"Video streaming error: {e}")
            await websocket.send_json({
                "type": "error",
                "message": f"Streaming error: {str(e)}"
            })
        finally:
            if cap is not None:
                cap.release()
            api_logger.info(f"Video stream ended. Processed {frame_count} frames")
