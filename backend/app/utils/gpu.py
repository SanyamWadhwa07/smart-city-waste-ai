"""
GPU detection and optimization utilities.

Handles device selection, FP16 configuration, and memory management.
"""

from __future__ import annotations

import os
from typing import Optional, Tuple

import torch


def is_cuda_available() -> bool:
    """Check if CUDA is available."""
    return torch.cuda.is_available()


def get_device(device_config: Optional[str] = None) -> str:
    """
    Get optimal device for inference.
    
    Args:
        device_config: Device configuration from env ("cpu", "cuda", "cuda:0")
                      If None, auto-detects best available device.
    
    Returns:
        Device string ("cpu" or "cuda")
    """
    if device_config is None:
        device_config = os.getenv("MODEL_DEVICE", "auto")
    
    if device_config == "auto":
        return "cuda" if is_cuda_available() else "cpu"
    
    # Validate cuda request
    if device_config.startswith("cuda"):
        if not is_cuda_available():
            print(f"Warning: CUDA requested but not available. Falling back to CPU.")
            return "cpu"
        return "cuda"  # Ultralytics handles cuda:N internally
    
    return "cpu"


def enable_fp16(device: str) -> bool:
    """
    Check if FP16 (half precision) should be enabled.
    
    FP16 is only beneficial on GPU with compute capability >= 7.0
    
    Args:
        device: Device string ("cpu" or "cuda")
    
    Returns:
        True if FP16 should be enabled
    """
    # Check environment override
    env_fp16 = os.getenv("ENABLE_FP16", "auto")
    if env_fp16 == "0" or env_fp16.lower() == "false":
        return False
    if env_fp16 == "1" or env_fp16.lower() == "true":
        return device == "cuda"
    
    # Auto-detect: enable on CUDA only
    if device == "cuda" and is_cuda_available():
        try:
            # Check compute capability
            capability = torch.cuda.get_device_capability(0)
            # FP16 beneficial on Volta (7.0) and newer
            return capability[0] >= 7
        except Exception:
            # Default to True for CUDA if can't detect
            return True
    
    return False


def get_device_info() -> dict:
    """
    Get detailed device information for logging.
    
    Returns:
        Dictionary with device details
    """
    info = {
        "cuda_available": is_cuda_available(),
        "device": get_device(),
        "fp16_enabled": enable_fp16(get_device()),
    }
    
    if is_cuda_available():
        try:
            info["cuda_version"] = torch.version.cuda
            info["gpu_count"] = torch.cuda.device_count()
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory"] = f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
            info["compute_capability"] = ".".join(map(str, torch.cuda.get_device_capability(0)))
        except Exception as e:
            info["cuda_error"] = str(e)
    
    return info


def optimize_memory(device: str) -> None:
    """
    Apply memory optimizations for inference.
    
    Args:
        device: Device string ("cpu" or "cuda")
    """
    if device == "cuda" and is_cuda_available():
        try:
            # Enable TF32 for faster computation on Ampere GPUs
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Enable cudnn autotuner for optimized convolution algorithms
            torch.backends.cudnn.benchmark = True
            
            # Empty cache
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"Warning: Could not apply memory optimizations: {e}")


def get_optimal_batch_size(device: str) -> int:
    """
    Get optimal batch size for classifier based on device.
    
    Args:
        device: Device string
    
    Returns:
        Recommended batch size
    """
    # Check environment override
    env_batch = os.getenv("BATCH_SIZE")
    if env_batch is not None:
        try:
            return int(env_batch)
        except ValueError:
            pass
    
    # Auto-detect based on device
    if device == "cuda" and is_cuda_available():
        try:
            # Estimate based on available memory
            mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            if mem_gb >= 16:
                return 32
            elif mem_gb >= 8:
                return 16
            else:
                return 8
        except Exception:
            return 8
    
    # CPU: smaller batches
    return 4


def get_optimal_num_workers(device: str) -> int:
    """
    Get optimal number of data loading workers.
    
    Args:
        device: Device string
    
    Returns:
        Number of workers
    """
    if device == "cuda":
        return 2  # GPU can handle more parallel loads
    return 0  # CPU: avoid overhead
