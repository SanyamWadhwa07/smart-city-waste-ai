"""
Error Handling & Custom Exceptions

Comprehensive error handling for all backend operations.
"""

from __future__ import annotations

from typing import Optional, Any
from enum import Enum
import traceback
import logging


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WasteAIException(Exception):
    """Base exception for all Waste AI errors."""
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_code: Optional[str] = None,
        details: Optional[dict] = None
    ):
        self.message = message
        self.severity = severity
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "details": self.details
        }


class ValidationError(WasteAIException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["invalid_value"] = str(value)
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.LOW,
            error_code="VALIDATION_ERROR",
            details=details
        )


class ModelInferenceError(WasteAIException):
    """Raised when model inference fails."""
    
    def __init__(self, message: str, model_name: Optional[str] = None):
        details = {}
        if model_name:
            details["model"] = model_name
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            error_code="INFERENCE_ERROR",
            details=details
        )


class ImageProcessingError(WasteAIException):
    """Raised when image processing fails."""
    
    def __init__(self, message: str, reason: Optional[str] = None):
        details = {}
        if reason:
            details["reason"] = reason
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            error_code="IMAGE_ERROR",
            details=details
        )


class CameraError(WasteAIException):
    """Raised when camera/video source fails."""
    
    def __init__(self, message: str, source: Optional[str] = None):
        details = {}
        if source:
            details["source"] = source
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            error_code="CAMERA_ERROR",
            details=details
        )


class ConfigurationError(WasteAIException):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, param: Optional[str] = None):
        details = {}
        if param:
            details["parameter"] = param
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.CRITICAL,
            error_code="CONFIG_ERROR",
            details=details
        )


class ResourceNotFoundError(WasteAIException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.LOW,
            error_code="NOT_FOUND",
            details=details
        )


class ContaminationDetectionError(WasteAIException):
    """Raised when contamination detection logic fails."""
    
    def __init__(self, message: str, reason: Optional[str] = None):
        details = {}
        if reason:
            details["reason"] = reason
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            error_code="CONTAMINATION_ERROR",
            details=details
        )


class ErrorHandler:
    """Centralized error handling and logging."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_exception(
        self,
        exc: Exception,
        context: Optional[str] = None,
        log_traceback: bool = True
    ) -> dict:
        """
        Handle an exception and return error response.
        
        Args:
            exc: Exception to handle
            context: Optional context string for logging
            log_traceback: Whether to log full traceback
        
        Returns:
            Dictionary with error information for API response
        """
        # If it's our custom exception, use its structured data
        if isinstance(exc, WasteAIException):
            error_response = exc.to_dict()
            log_level = self._severity_to_log_level(exc.severity)
        else:
            # Generic exception handling
            error_response = {
                "error": "INTERNAL_ERROR",
                "message": str(exc) or "An unexpected error occurred",
                "severity": ErrorSeverity.HIGH.value,
                "details": {}
            }
            log_level = logging.ERROR
        
        # Log the error
        log_message = f"[{context}] {error_response['message']}" if context else error_response["message"]
        
        if log_traceback:
            self.logger.log(log_level, log_message, exc_info=True)
        else:
            self.logger.log(log_level, log_message)
        
        # Add traceback to details in development
        if log_traceback and not isinstance(exc, WasteAIException):
            error_response["details"]["traceback"] = traceback.format_exc()
        
        return error_response
    
    @staticmethod
    def _severity_to_log_level(severity: ErrorSeverity) -> int:
        """Convert error severity to logging level."""
        mapping = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        return mapping.get(severity, logging.ERROR)
    
    def safe_execute(self, func, *args, default=None, context: Optional[str] = None, **kwargs):
        """
        Safely execute a function with error handling.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            default: Default value to return on error
            context: Context string for logging
            **kwargs: Keyword arguments for func
        
        Returns:
            Function result or default value on error
        """
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            self.handle_exception(exc, context=context or func.__name__)
            return default


class SafetyChecks:
    """Safety checks and circuit breakers for production systems."""
    
    @staticmethod
    def check_confidence_anomaly(confidence: float, history: list[float], threshold: float = 0.3) -> bool:
        """
        Check if confidence score is anomalously different from recent history.
        
        Args:
            confidence: Current confidence score
            history: List of recent confidence scores
            threshold: Maximum allowed deviation
        
        Returns:
            True if confidence is anomalous
        """
        if not history:
            return False
        
        avg = sum(history) / len(history)
        deviation = abs(confidence - avg)
        
        return deviation > threshold
    
    @staticmethod
    def check_rate_limit(
        current_count: int,
        time_window: float,
        max_per_window: int
    ) -> tuple[bool, str]:
        """
        Check if a rate limit has been exceeded.
        
        Args:
            current_count: Current request count in window
            time_window: Time window in seconds
            max_per_window: Maximum allowed requests
        
        Returns:
            (is_limited, message)
        """
        if current_count >= max_per_window:
            return True, f"Rate limit exceeded: {current_count}/{max_per_window} in {time_window}s"
        return False, ""
    
    @staticmethod
    def check_contamination_threshold(
        contamination_rate: float,
        threshold: float = 0.30
    ) -> tuple[bool, str]:
        """
        Check if contamination rate exceeds threshold.
        
        Args:
            contamination_rate: Current contamination rate (0-1)
            threshold: Maximum acceptable rate
        
        Returns:
            (is_critical, alert_message)
        """
        if contamination_rate >= threshold:
            return True, f"CRITICAL: Contamination rate {contamination_rate:.1%} exceeds threshold {threshold:.1%}"
        return False, ""
    
    @staticmethod
    def validate_model_output(
        label: Optional[str],
        confidence: Optional[float],
        bbox: Optional[list]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that model output is usable.
        
        Returns:
            (is_valid, error_message)
        """
        if not label:
            return False, "Model returned no label"
        
        if confidence is None or confidence < 0:
            return False, f"Invalid confidence: {confidence}"
        
        if bbox and len(bbox) != 4:
            return False, f"Invalid bbox format: {bbox}"
        
        return True, None
