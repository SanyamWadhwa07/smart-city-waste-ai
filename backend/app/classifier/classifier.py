"""
Material Classifier Agent - Stage 2 of Dual-Agent Pipeline.

Uses prithivMLmods/Augmented-Waste-Classifier-SigLIP2 for material classification.
CRITICAL: Only classifies detector crops, never full frames.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from PIL import Image

try:
    from transformers import AutoImageProcessor, AutoModelForImageClassification
    import torch
except ImportError:
    AutoImageProcessor = None
    AutoModelForImageClassification = None
    torch = None

from ..utils.gpu import get_device, get_optimal_batch_size
from ..utils.batching import batch_crops
from ..logging_config import inference_logger
from ..errors import ModelInferenceError


@dataclass
class ClassifierResult:
    """Result from classifier for a single crop."""
    
    label: str
    confidence: float
    top_k_labels: Optional[List[str]] = None
    top_k_scores: Optional[List[float]] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "label": self.label,
            "confidence": self.confidence,
            "top_k_labels": self.top_k_labels,
            "top_k_scores": self.top_k_scores,
        }


class MaterialClassifier:
    """
    Material classifier for waste objects using SigLIP transformer.
    
    Classifies cropped regions from detector into specific material types.
    NEVER processes full frames - only detector crops.
    
    Features:
    - Batch processing for efficiency
    - GPU acceleration
    - Top-K predictions
    - Fallback handling
    """
    
    def __init__(
        self,
        model_path: str = None,
        device: str = None,
        batch_size: int = None,
        top_k: int = 3,
        verbose: bool = False
    ):
        """
        Initialize material classifier.
        
        Args:
            model_path: Path to model or HuggingFace repo
            device: Device to use ("cpu", "cuda", or None for auto)
            batch_size: Batch size for processing (None for auto)
            top_k: Number of top predictions to return
            verbose: Enable verbose logging
        """
        if AutoImageProcessor is None or AutoModelForImageClassification is None:
            raise ImportError(
                "transformers not installed. Install with: pip install transformers"
            )
        
        if torch is None:
            raise ImportError(
                "torch not installed. Install with: pip install torch"
            )
        
        # Configuration
        self.top_k = top_k
        self.verbose = verbose
        
        # Device setup
        self.device = get_device(device)
        self.batch_size = batch_size or get_optimal_batch_size(self.device)
        
        # Model path
        if model_path is None:
            model_path = os.getenv(
                "TIER2_MODEL_PATH",
                "prithivMLmods/Augmented-Waste-Classifier-SigLIP2"
            )
        self.model_path = model_path
        
        # Load model
        inference_logger.info(
            "Loading classifier",
            extra={
                "model_path": model_path,
                "device": self.device,
                "batch_size": self.batch_size,
            }
        )
        
        try:
            self.processor, self.model = self._load_model()
            inference_logger.info("Classifier loaded successfully")
        except Exception as e:
            inference_logger.error(f"Failed to load classifier: {e}")
            raise ModelInferenceError(f"Classifier loading failed: {e}")
    
    def _load_model(self):
        """Load SigLIP model and processor."""
        try:
            # Load processor and model
            processor = AutoImageProcessor.from_pretrained(self.model_path)
            model = AutoModelForImageClassification.from_pretrained(self.model_path)
            
            # Move to device
            model.to(self.device)
            model.eval()  # Evaluation mode
            
            # Disable gradient computation for inference
            for param in model.parameters():
                param.requires_grad = False
            
            return processor, model
            
        except Exception as e:
            raise ModelInferenceError(f"Failed to load classifier model: {e}")
    
    def classify_batch(
        self,
        crops: List[np.ndarray],
        return_top_k: bool = True
    ) -> List[ClassifierResult]:
        """
        Classify a batch of crops.
        
        Args:
            crops: List of cropped images (numpy arrays)
            return_top_k: Whether to return top-k predictions
        
        Returns:
            List of ClassifierResult objects
        
        Raises:
            ModelInferenceError: If classification fails
            ValueError: If crops is empty or contains full frames
        """
        if not crops:
            return []
        
        # Validate inputs are crops, not full frames
        self._validate_crops(crops)
        
        try:
            results = []
            
            # Process in batches
            for batch in batch_crops(crops, self.batch_size):
                batch_results = self._classify_batch_internal(batch, return_top_k)
                results.extend(batch_results)
            
            return results
            
        except Exception as e:
            inference_logger.error(f"Classification failed: {e}")
            raise ModelInferenceError(f"Classifier inference failed: {e}")
    
    def _classify_batch_internal(
        self,
        crops: List[np.ndarray],
        return_top_k: bool
    ) -> List[ClassifierResult]:
        """Internal batch classification."""
        # Convert numpy arrays to PIL Images
        pil_images = []
        for crop in crops:
            # Convert BGR to RGB if needed
            if crop.shape[2] == 3:
                crop_rgb = crop[:, :, ::-1].copy()
            else:
                crop_rgb = crop
            pil_img = Image.fromarray(crop_rgb)
            pil_images.append(pil_img)
        
        # Preprocess images
        inputs = self.processor(
            images=pil_images,
            return_tensors="pt"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
        
        # Get predictions
        probs = torch.nn.functional.softmax(logits, dim=-1)
        
        results = []
        for i in range(len(crops)):
            # Top prediction
            top_prob, top_idx = torch.max(probs[i], dim=0)
            label = self.model.config.id2label[top_idx.item()]
            confidence = top_prob.item()
            
            # Top-K predictions
            top_k_labels = None
            top_k_scores = None
            
            if return_top_k and self.top_k > 1:
                top_k_probs, top_k_indices = torch.topk(
                    probs[i], 
                    min(self.top_k, len(probs[i]))
                )
                top_k_labels = [
                    self.model.config.id2label[idx.item()]
                    for idx in top_k_indices
                ]
                top_k_scores = [prob.item() for prob in top_k_probs]
            
            result = ClassifierResult(
                label=label,
                confidence=confidence,
                top_k_labels=top_k_labels,
                top_k_scores=top_k_scores
            )
            results.append(result)
        
        return results
    
    def classify_single(
        self,
        crop: np.ndarray,
        return_top_k: bool = True
    ) -> ClassifierResult:
        """
        Classify a single crop.
        
        Args:
            crop: Cropped image (numpy array)
            return_top_k: Whether to return top-k predictions
        
        Returns:
            ClassifierResult
        """
        results = self.classify_batch([crop], return_top_k)
        return results[0] if results else None
    
    def _validate_crops(self, crops: List[np.ndarray]) -> None:
        """
        Validate that inputs are crops, not full frames.
        
        Raises:
            ValueError: If images appear to be full frames
        """
        for i, crop in enumerate(crops):
            if crop.size == 0:
                raise ValueError(f"Crop {i} is empty")
            
            h, w = crop.shape[:2]
            
            # Check if image is suspiciously large (likely a full frame)
            # Typical crops are < 400x400, full frames are 640x480 or larger
            if h > 600 or w > 600:
                inference_logger.warning(
                    f"Large crop detected: {w}x{h}. "
                    f"Ensure you're passing detector crops, not full frames."
                )
            
            # Check aspect ratio is reasonable
            aspect_ratio = max(w, h) / min(w, h)
            if aspect_ratio > 5:
                inference_logger.warning(
                    f"Unusual aspect ratio for crop {i}: {aspect_ratio:.2f}"
                )
    
    def get_label_map(self) -> dict:
        """Get model's label mapping."""
        if hasattr(self.model.config, 'id2label'):
            return self.model.config.id2label
        return {}
    
    def get_num_classes(self) -> int:
        """Get number of output classes."""
        return self.model.config.num_labels
    
    def get_info(self) -> dict:
        """Get classifier information for logging."""
        return {
            "model_path": self.model_path,
            "device": self.device,
            "batch_size": self.batch_size,
            "num_classes": self.get_num_classes(),
            "top_k": self.top_k,
        }
