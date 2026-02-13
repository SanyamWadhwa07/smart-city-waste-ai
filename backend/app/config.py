"""
Centralized configuration management for waste intelligence backend.

Loads and validates all configuration from environment variables.
Uses Pydantic for type-safe config with validation and defaults.
"""

from __future__ import annotations

import os
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator


class ModelConfig(BaseModel):
    """Model configuration."""
    
    tier1_model_path: str = Field(
        default="models/yolov8m-seg.pt",
        description="Path to Tier-1 detector model (turhancan97 segmentation)"
    )
    tier2_model_path: str = Field(
        default="prithivMLmods/Augmented-Waste-Classifier-SigLIP2",
        description="Path to Tier-2 classifier model"
    )
    device: str = Field(
        default="auto",
        description="Device for inference (cpu, cuda, auto)"
    )
    enable_fp16: str = Field(
        default="auto",
        description="Enable FP16 (0, 1, auto)"
    )
    image_size: int = Field(
        default=640,
        description="Image size for detector",
        ge=320,
        le=1280
    )
    batch_size: Optional[int] = Field(
        default=None,
        description="Batch size for classifier (None for auto)"
    )
    warmup_frames: int = Field(
        default=10,
        description="Number of warmup frames",
        ge=0,
        le=100
    )
    
    @classmethod
    def from_env(cls) -> ModelConfig:
        """Load from environment variables."""
        return cls(
            tier1_model_path=os.getenv("TIER1_MODEL_PATH", cls.__fields__["tier1_model_path"].default),
            tier2_model_path=os.getenv("TIER2_MODEL_PATH", cls.__fields__["tier2_model_path"].default),
            device=os.getenv("MODEL_DEVICE", cls.__fields__["device"].default),
            enable_fp16=os.getenv("ENABLE_FP16", cls.__fields__["enable_fp16"].default),
            image_size=int(os.getenv("MODEL_IMGSZ", str(cls.__fields__["image_size"].default))),
            batch_size=int(os.getenv("BATCH_SIZE")) if os.getenv("BATCH_SIZE") else None,
            warmup_frames=int(os.getenv("WARMUP_FRAMES", str(cls.__fields__["warmup_frames"].default))),
        )


class ThresholdConfig(BaseModel):
    """Confidence threshold configuration."""
    
    detector_confidence: float = Field(
        default=0.40,
        description="Detector confidence threshold",
        ge=0.0,
        le=1.0
    )
    classifier_confidence: float = Field(
        default=0.55,
        description="Classifier confidence threshold",
        ge=0.0,
        le=1.0
    )
    high_confidence: float = Field(
        default=0.70,
        description="High confidence threshold for final material selection",
        ge=0.0,
        le=1.0
    )
    iou_threshold: float = Field(
        default=0.45,
        description="IoU threshold for NMS",
        ge=0.0,
        le=1.0
    )
    contamination_threshold: float = Field(
        default=0.30,
        description="Contamination score threshold",
        ge=0.0,
        le=1.0
    )
    
    @classmethod
    def from_env(cls) -> ThresholdConfig:
        """Load from environment variables."""
        return cls(
            detector_confidence=float(os.getenv("MODEL_CONF_TIER1", str(cls.__fields__["detector_confidence"].default))),
            classifier_confidence=float(os.getenv("MODEL_CONF_TIER2", str(cls.__fields__["classifier_confidence"].default))),
            high_confidence=float(os.getenv("HIGH_CONF_THRESHOLD", str(cls.__fields__["high_confidence"].default))),
            iou_threshold=float(os.getenv("MODEL_IOU_THRESHOLD", str(cls.__fields__["iou_threshold"].default))),
            contamination_threshold=float(os.getenv("CONTAMINATION_THRESHOLD", str(cls.__fields__["contamination_threshold"].default))),
        )


class CameraConfig(BaseModel):
    """Camera configuration."""
    
    source: int | str = Field(
        default=0,
        description="Camera source (index or video path)"
    )
    fps_limit: float = Field(
        default=30.0,
        description="FPS limit for streaming",
        ge=1.0,
        le=60.0
    )
    
    @classmethod
    def from_env(cls) -> CameraConfig:
        """Load from environment variables."""
        source = os.getenv("CAMERA_SOURCE", "0")
        # Try to parse as int, otherwise use as string (video path)
        try:
            source = int(source)
        except ValueError:
            pass
        
        return cls(
            source=source,
            fps_limit=float(os.getenv("CAMERA_FPS_LIMIT", str(cls.__fields__["fps_limit"].default))),
        )


class RoutingConfig(BaseModel):
    """Routing engine configuration."""
    
    uncertain_to_review: bool = Field(
        default=True,
        description="Send uncertain items to manual review"
    )
    contamination_to_review: bool = Field(
        default=False,
        description="Send contaminated items to manual review"
    )
    
    @classmethod
    def from_env(cls) -> RoutingConfig:
        """Load from environment variables."""
        return cls(
            uncertain_to_review=os.getenv("UNCERTAIN_TO_REVIEW", "1") == "1",
            contamination_to_review=os.getenv("CONTAMINATION_TO_REVIEW", "0") == "1",
        )


class TaxonomyConfig(BaseModel):
    """Taxonomy configuration."""
    
    config_path: Optional[str] = Field(
        default=None,
        description="Path to custom taxonomy JSON"
    )
    
    @classmethod
    def from_env(cls) -> TaxonomyConfig:
        """Load from environment variables."""
        return cls(
            config_path=os.getenv("TAXONOMY_CONFIG_PATH"),
        )


class AppConfig(BaseModel):
    """Complete application configuration."""
    
    use_real_inference: bool = Field(
        default=True,
        description="Use real inference vs simulation"
    )
    model: ModelConfig
    thresholds: ThresholdConfig
    camera: CameraConfig
    routing: RoutingConfig
    taxonomy: TaxonomyConfig
    verbose: bool = Field(
        default=False,
        description="Enable verbose logging"
    )
    
    @classmethod
    def from_env(cls) -> AppConfig:
        """Load complete configuration from environment."""
        return cls(
            use_real_inference=os.getenv("USE_REAL_INFERENCE", "1") == "1",
            model=ModelConfig.from_env(),
            thresholds=ThresholdConfig.from_env(),
            camera=CameraConfig.from_env(),
            routing=RoutingConfig.from_env(),
            taxonomy=TaxonomyConfig.from_env(),
            verbose=os.getenv("VERBOSE", "0") == "1",
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.dict()


# Global config instance (lazy loaded)
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config


def reload_config() -> AppConfig:
    """Reload configuration from environment."""
    global _config
    _config = AppConfig.from_env()
    return _config


# Convenience functions for direct access
def get_model_config() -> ModelConfig:
    """Get model configuration."""
    return get_config().model


def get_threshold_config() -> ThresholdConfig:
    """Get threshold configuration."""
    return get_config().thresholds


def get_camera_config() -> CameraConfig:
    """Get camera configuration."""
    return get_config().camera


def get_routing_config() -> RoutingConfig:
    """Get routing configuration."""
    return get_config().routing


def get_taxonomy_config() -> TaxonomyConfig:
    """Get taxonomy configuration."""
    return get_config().taxonomy
