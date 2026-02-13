"""
Model warmup utilities.

Runs dummy inference to initialize models and optimize CUDA kernels.
"""

from __future__ import annotations

import os
from typing import Callable, Optional
import numpy as np
import time


def create_dummy_frame(
    height: int = 640,
    width: int = 640,
    channels: int = 3
) -> np.ndarray:
    """
    Create a dummy frame for warmup.
    
    Args:
        height: Frame height
        width: Frame width
        channels: Number of channels (3 for RGB)
    
    Returns:
        Random numpy array simulating a frame
    """
    return np.random.randint(0, 255, (height, width, channels), dtype=np.uint8)


def warmup_model(
    inference_func: Callable[[np.ndarray], any],
    num_frames: int = None,
    frame_size: tuple[int, int] = (640, 640),
    verbose: bool = True
) -> dict[str, float]:
    """
    Warmup model with dummy inference runs.
    
    First few inference runs are slower due to CUDA kernel compilation,
    memory allocation, and model initialization. Warmup ensures consistent
    performance for production inference.
    
    Args:
        inference_func: Function that takes a frame and runs inference
        num_frames: Number of warmup frames. If None, uses WARMUP_FRAMES env var.
        frame_size: (height, width) of dummy frames
        verbose: Whether to print progress
    
    Returns:
        Dictionary with warmup statistics
    """
    if num_frames is None:
        num_frames = int(os.getenv("WARMUP_FRAMES", "10"))
    
    if num_frames <= 0:
        return {"warmup_frames": 0, "avg_time_ms": 0.0}
    
    if verbose:
        print(f"Warming up model with {num_frames} dummy frames...")
    
    h, w = frame_size
    times = []
    
    for i in range(num_frames):
        dummy_frame = create_dummy_frame(h, w)
        
        start = time.perf_counter()
        try:
            _ = inference_func(dummy_frame)
        except Exception as e:
            if verbose:
                print(f"Warning: Warmup frame {i+1} failed: {e}")
            continue
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        times.append(elapsed_ms)
        
        if verbose and (i + 1) % 5 == 0:
            print(f"  Warmup {i+1}/{num_frames}: {elapsed_ms:.1f}ms")
    
    if not times:
        return {"warmup_frames": 0, "avg_time_ms": 0.0, "error": "All warmup frames failed"}
    
    stats = {
        "warmup_frames": len(times),
        "avg_time_ms": sum(times) / len(times),
        "min_time_ms": min(times),
        "max_time_ms": max(times),
        "last_time_ms": times[-1],
    }
    
    if verbose:
        print(f"Warmup complete: avg={stats['avg_time_ms']:.1f}ms, "
              f"last={stats['last_time_ms']:.1f}ms")
    
    return stats


def warmup_detector(
    detector,
    num_frames: int = None,
    image_size: int = 640,
    verbose: bool = True
) -> dict[str, float]:
    """
    Warmup YOLO detector.
    
    Args:
        detector: Detector instance with detect() method
        num_frames: Number of warmup frames
        image_size: Image size for detection
        verbose: Whether to print progress
    
    Returns:
        Warmup statistics
    """
    def detect_func(frame):
        return detector.detect(frame)
    
    return warmup_model(
        detect_func,
        num_frames=num_frames,
        frame_size=(image_size, image_size),
        verbose=verbose
    )


def warmup_classifier(
    classifier,
    num_batches: int = None,
    crop_size: int = 224,
    batch_size: int = 4,
    verbose: bool = True
) -> dict[str, float]:
    """
    Warmup classifier with dummy crops.
    
    Args:
        classifier: Classifier instance with classify_batch() method
        num_batches: Number of warmup batches. If None, uses WARMUP_FRAMES.
        crop_size: Size of crops
        batch_size: Number of crops per batch
        verbose: Whether to print progress
    
    Returns:
        Warmup statistics
    """
    if num_batches is None:
        num_batches = int(os.getenv("WARMUP_FRAMES", "10")) // batch_size
        num_batches = max(1, num_batches)
    
    if verbose:
        print(f"Warming up classifier with {num_batches} batches...")
    
    times = []
    
    for i in range(num_batches):
        # Create batch of dummy crops
        crops = [
            create_dummy_frame(crop_size, crop_size)
            for _ in range(batch_size)
        ]
        
        start = time.perf_counter()
        try:
            _ = classifier.classify_batch(crops)
        except Exception as e:
            if verbose:
                print(f"Warning: Warmup batch {i+1} failed: {e}")
            continue
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        times.append(elapsed_ms)
        
        if verbose and (i + 1) % 3 == 0:
            print(f"  Warmup batch {i+1}/{num_batches}: {elapsed_ms:.1f}ms")
    
    if not times:
        return {"warmup_batches": 0, "avg_time_ms": 0.0, "error": "All warmup batches failed"}
    
    stats = {
        "warmup_batches": len(times),
        "avg_time_ms": sum(times) / len(times),
        "min_time_ms": min(times),
        "max_time_ms": max(times),
        "last_time_ms": times[-1],
    }
    
    if verbose:
        print(f"Warmup complete: avg={stats['avg_time_ms']:.1f}ms, "
              f"last={stats['last_time_ms']:.1f}ms")
    
    return stats


def warmup_pipeline(
    pipeline,
    num_frames: int = None,
    verbose: bool = True
) -> dict[str, any]:
    """
    Warmup complete inference pipeline.
    
    Args:
        pipeline: Pipeline instance with analyze_frame() method
        num_frames: Number of warmup frames
        verbose: Whether to print progress
    
    Returns:
        Warmup statistics including per-stage timing
    """
    if num_frames is None:
        num_frames = int(os.getenv("WARMUP_FRAMES", "10"))
    
    if verbose:
        print(f"Warming up complete pipeline with {num_frames} frames...")
    
    stats = warmup_model(
        lambda frame: pipeline.analyze_frame(frame),
        num_frames=num_frames,
        verbose=verbose
    )
    
    return stats
