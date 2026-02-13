"""
Input Validation & Sanitization Module

Comprehensive validation for all inputs to prevent edge cases and ensure data integrity.
"""

from __future__ import annotations

import re
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    error_message: Optional[str] = None
    sanitized_value: Any = None


class InputValidator:
    """Centralized validation logic for all backend inputs."""
    
    # Valid material categories
    VALID_TIER1_LABELS = {
        "BIODEGRADABLE", "CARDBOARD", "GLASS", "METAL", "PAPER", "PLASTIC",
        "HAZARDOUS", "LANDFILL", "UNKNOWN"
    }
    
    VALID_TIER2_LABELS = {
        "battery", "biological", "cardboard", "clothes", "glass", "metal",
        "paper", "plastic", "shoes", "trash", "e-waste", "medical", "green-glass", "unknown"
    }
    
    VALID_ROUTES = {
        "ORGANIC", "PLASTIC_BIN", "PAPER_BIN", "METAL_BIN", "GLASS_BIN",
        "HAZARDOUS", "LANDFILL", "MANUAL_REVIEW"
    }
    
    VALID_REVIEW_STATUSES = {"pending", "approved", "rejected", "escalated"}
    
    @staticmethod
    def validate_confidence(confidence: float) -> ValidationResult:
        """Validate confidence score is between 0 and 1."""
        if not isinstance(confidence, (int, float)):
            return ValidationResult(
                is_valid=False,
                error_message=f"Confidence must be a number, got {type(confidence).__name__}"
            )
        
        if not 0.0 <= confidence <= 1.0:
            return ValidationResult(
                is_valid=False,
                error_message=f"Confidence must be between 0 and 1, got {confidence}"
            )
        
        # Sanitize to reasonable precision
        sanitized = round(float(confidence), 4)
        return ValidationResult(is_valid=True, sanitized_value=sanitized)
    
    @staticmethod
    def validate_bbox(bbox: list[float]) -> ValidationResult:
        """
        Validate bounding box format [x, y, w, h] with normalized coordinates.
        All values should be between 0 and 1.
        """
        if not isinstance(bbox, (list, tuple)):
            return ValidationResult(
                is_valid=False,
                error_message=f"BBox must be a list, got {type(bbox).__name__}"
            )
        
        if len(bbox) != 4:
            return ValidationResult(
                is_valid=False,
                error_message=f"BBox must have exactly 4 values [x,y,w,h], got {len(bbox)}"
            )
        
        for i, val in enumerate(bbox):
            if not isinstance(val, (int, float)):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"BBox value at index {i} must be a number, got {type(val).__name__}"
                )
            
            if not 0.0 <= val <= 1.0:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"BBox values must be normalized (0-1), got {val} at index {i}"
                )
        
        # Validate logical constraints
        x, y, w, h = bbox
        if x + w > 1.0 or y + h > 1.0:
            return ValidationResult(
                is_valid=False,
                error_message=f"BBox extends beyond image bounds: x+w={x+w}, y+h={y+h}"
            )
        
        if w <= 0 or h <= 0:
            return ValidationResult(
                is_valid=False,
                error_message=f"BBox width and height must be positive, got w={w}, h={h}"
            )
        
        # Sanitize to reasonable precision
        sanitized = [round(float(v), 4) for v in bbox]
        return ValidationResult(is_valid=True, sanitized_value=sanitized)
    
    @staticmethod
    def validate_label(label: str, tier: int = 1) -> ValidationResult:
        """
        Validate material label against known categories.
        
        Args:
            label: Material label to validate
            tier: 1 for tier1 (6 classes), 2 for tier2 (10+ classes)
        """
        if not isinstance(label, str):
            return ValidationResult(
                is_valid=False,
                error_message=f"Label must be a string, got {type(label).__name__}"
            )
        
        if not label or not label.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Label cannot be empty"
            )
        
        # Sanitize: trim whitespace, normalize case
        if tier == 1:
            sanitized = label.strip().upper()
            valid_set = InputValidator.VALID_TIER1_LABELS
        else:
            sanitized = label.strip().lower()
            valid_set = InputValidator.VALID_TIER2_LABELS
        
        # Check against known labels (allow unknown for flexibility)
        if sanitized not in valid_set and sanitized.upper() not in {"UNKNOWN"}:
            # Log warning but don't fail - new materials may be added
            return ValidationResult(
                is_valid=True,  # Allow but sanitize
                sanitized_value=sanitized,
                error_message=f"Warning: Unknown label '{sanitized}' (tier {tier})"
            )
        
        return ValidationResult(is_valid=True, sanitized_value=sanitized)
    
    @staticmethod
    def validate_route(route: str) -> ValidationResult:
        """Validate routing decision against valid routes."""
        if not isinstance(route, str):
            return ValidationResult(
                is_valid=False,
                error_message=f"Route must be a string, got {type(route).__name__}"
            )
        
        sanitized = route.strip().upper()
        
        if sanitized not in InputValidator.VALID_ROUTES:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid route '{route}'. Valid routes: {InputValidator.VALID_ROUTES}"
            )
        
        return ValidationResult(is_valid=True, sanitized_value=sanitized)
    
    @staticmethod
    def validate_event_id(event_id: str) -> ValidationResult:
        """Validate event ID format and sanitize."""
        if not isinstance(event_id, str):
            return ValidationResult(
                is_valid=False,
                error_message=f"Event ID must be a string, got {type(event_id).__name__}"
            )
        
        if not event_id or not event_id.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Event ID cannot be empty"
            )
        
        # Sanitize: alphanumeric, dashes, underscores only
        sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', event_id.strip())
        
        if not sanitized:
            return ValidationResult(
                is_valid=False,
                error_message="Event ID must contain alphanumeric characters"
            )
        
        if len(sanitized) > 100:
            return ValidationResult(
                is_valid=False,
                error_message=f"Event ID too long: {len(sanitized)} chars (max 100)"
            )
        
        return ValidationResult(is_valid=True, sanitized_value=sanitized)
    
    @staticmethod
    def validate_timestamp(timestamp: float) -> ValidationResult:
        """Validate timestamp is a reasonable Unix timestamp."""
        if not isinstance(timestamp, (int, float)):
            return ValidationResult(
                is_valid=False,
                error_message=f"Timestamp must be a number, got {type(timestamp).__name__}"
            )
        
        # Reasonable range: 2020-01-01 to 2050-12-31
        MIN_TIMESTAMP = 1577836800  # 2020-01-01
        MAX_TIMESTAMP = 2556144000  # 2050-12-31
        
        if not MIN_TIMESTAMP <= timestamp <= MAX_TIMESTAMP:
            return ValidationResult(
                is_valid=False,
                error_message=f"Timestamp out of reasonable range: {timestamp}"
            )
        
        return ValidationResult(is_valid=True, sanitized_value=float(timestamp))
    
    @staticmethod
    def validate_review_status(status: str) -> ValidationResult:
        """Validate review status value."""
        if not isinstance(status, str):
            return ValidationResult(
                is_valid=False,
                error_message=f"Status must be a string, got {type(status).__name__}"
            )
        
        sanitized = status.strip().lower()
        
        if sanitized not in InputValidator.VALID_REVIEW_STATUSES:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid status '{status}'. Valid: {InputValidator.VALID_REVIEW_STATUSES}"
            )
        
        return ValidationResult(is_valid=True, sanitized_value=sanitized)
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 500) -> str:
        """Sanitize string input: trim, limit length, remove control characters."""
        if not isinstance(value, str):
            return ""
        
        # Remove control characters except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', value)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized


class DetectionValidator:
    """Specialized validation for detection objects."""
    
    @staticmethod
    def validate_detection(detection: dict) -> ValidationResult:
        """Validate complete detection object."""
        required_fields = ["label", "confidence", "bbox"]
        
        # Check required fields
        for field in required_fields:
            if field not in detection:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Missing required field: {field}"
                )
        
        # Validate label
        label_result = InputValidator.validate_label(detection["label"])
        if not label_result.is_valid:
            return label_result
        
        # Validate confidence
        conf_result = InputValidator.validate_confidence(detection["confidence"])
        if not conf_result.is_valid:
            return conf_result
        
        # Validate bbox
        bbox_result = InputValidator.validate_bbox(detection["bbox"])
        if not bbox_result.is_valid:
            return bbox_result
        
        # Return sanitized detection
        sanitized = {
            "label": label_result.sanitized_value,
            "confidence": conf_result.sanitized_value,
            "bbox": bbox_result.sanitized_value
        }
        
        return ValidationResult(is_valid=True, sanitized_value=sanitized)
    
    @staticmethod
    def is_detection_reliable(confidence: float, threshold: float = 0.5) -> bool:
        """Check if detection confidence is above reliability threshold."""
        return confidence >= threshold
    
    @staticmethod
    def is_bbox_reasonable(bbox: list[float], min_size: float = 0.01) -> bool:
        """
        Check if bounding box is reasonable size (not too small).
        
        Args:
            bbox: [x, y, w, h] normalized coordinates
            min_size: Minimum width/height as fraction of image (default 1%)
        """
        if len(bbox) != 4:
            return False
        
        _, _, w, h = bbox
        return w >= min_size and h >= min_size
