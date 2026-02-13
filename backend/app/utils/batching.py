"""
Batching utilities for efficient classifier inference.

Handles grouping crops into batches to reduce inference overhead.
"""

from __future__ import annotations

from typing import List, Iterator, TypeVar
import numpy as np

T = TypeVar('T')


def batch_crops(
    crops: List[np.ndarray],
    batch_size: int = 8
) -> Iterator[List[np.ndarray]]:
    """
    Batch image crops for efficient processing.
    
    Args:
        crops: List of image crops (each a numpy array)
        batch_size: Maximum batch size
    
    Yields:
        Batches of crops
    
    Example:
        >>> crops = [img1, img2, img3, img4, img5]
        >>> for batch in batch_crops(crops, batch_size=2):
        ...     process_batch(batch)  # [img1, img2], [img3, img4], [img5]
    """
    for i in range(0, len(crops), batch_size):
        yield crops[i:i + batch_size]


def batch_items(items: List[T], batch_size: int) -> Iterator[List[T]]:
    """
    Generic batching utility.
    
    Args:
        items: List of items to batch
        batch_size: Maximum batch size
    
    Yields:
        Batches of items
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


class BatchProcessor:
    """
    Stateful batch processor with configurable batch size.
    
    Accumulates items and processes them in batches when threshold is reached.
    Useful for streaming scenarios where items arrive one at a time.
    """
    
    def __init__(self, batch_size: int = 8, processor=None):
        """
        Initialize batch processor.
        
        Args:
            batch_size: Maximum items per batch
            processor: Optional callable to process each batch
        """
        self.batch_size = batch_size
        self.processor = processor
        self.buffer: List = []
        self.results: List = []
    
    def add(self, item) -> None:
        """Add item to buffer."""
        self.buffer.append(item)
    
    def should_process(self) -> bool:
        """Check if buffer has reached batch size."""
        return len(self.buffer) >= self.batch_size
    
    def process(self) -> List:
        """
        Process current buffer.
        
        Returns:
            List of processed results (or raw buffer if no processor)
        """
        if not self.buffer:
            return []
        
        if self.processor is not None:
            results = self.processor(self.buffer)
        else:
            results = self.buffer.copy()
        
        self.buffer.clear()
        return results
    
    def process_if_ready(self) -> List:
        """Process buffer only if batch size reached."""
        if self.should_process():
            return self.process()
        return []
    
    def flush(self) -> List:
        """Process remaining items in buffer."""
        return self.process()
    
    def __len__(self) -> int:
        """Get current buffer size."""
        return len(self.buffer)


def pad_batch(
    images: List[np.ndarray],
    target_size: tuple[int, int] = None
) -> np.ndarray:
    """
    Pad images to same size for batching.
    
    Args:
        images: List of images with potentially different sizes
        target_size: Optional target (height, width). If None, uses max dimensions.
    
    Returns:
        Stacked batch as numpy array [B, H, W, C]
    """
    if not images:
        return np.array([])
    
    # Determine target size
    if target_size is None:
        max_h = max(img.shape[0] for img in images)
        max_w = max(img.shape[1] for img in images)
        target_size = (max_h, max_w)
    
    target_h, target_w = target_size
    
    # Pad all images
    padded = []
    for img in images:
        h, w = img.shape[:2]
        
        if len(img.shape) == 3:
            c = img.shape[2]
            padded_img = np.zeros((target_h, target_w, c), dtype=img.dtype)
        else:
            padded_img = np.zeros((target_h, target_w), dtype=img.dtype)
        
        padded_img[:h, :w] = img
        padded.append(padded_img)
    
    return np.array(padded)


def estimate_batch_size_for_memory(
    image_size: tuple[int, int],
    channels: int = 3,
    dtype_size: int = 4,  # float32
    available_memory_gb: float = 2.0
) -> int:
    """
    Estimate maximum batch size based on available memory.
    
    Args:
        image_size: (height, width) of images
        channels: Number of channels
        dtype_size: Bytes per element (4 for float32, 2 for float16)
        available_memory_gb: Available GPU/CPU memory in GB
    
    Returns:
        Estimated maximum batch size
    """
    h, w = image_size
    bytes_per_image = h * w * channels * dtype_size
    
    # Use 80% of available memory for safety
    usable_memory = available_memory_gb * 1e9 * 0.8
    
    max_batch = int(usable_memory / bytes_per_image)
    
    # Clamp to reasonable range
    return max(1, min(max_batch, 64))
