"""
Structured Logging System

Production-ready logging with context, performance tracking, and structured output.
"""

from __future__ import annotations

import logging
import time
import json
from typing import Optional, Any, Dict
from datetime import datetime
from contextlib import contextmanager
from functools import wraps
import sys


class StructuredLogger:
    """Enhanced logger with structured output and context."""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Add console handler with JSON formatter
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(StructuredFormatter()
)
            self.logger.addHandler(handler)
        
        self.context: Dict[str, Any] = {}
    
    def add_context(self, **kwargs):
        """Add persistent context to all log messages."""
        self.context.update(kwargs)
    
    def remove_context(self, *keys):
        """Remove context keys."""
        for key in keys:
            self.context.pop(key, None)
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log with added context."""
        extra = {"context": {**self.context, **kwargs}}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message."""
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    @contextmanager
    def operation(self, operation_name: str, **kwargs):
        """
        Context manager for logging operation start/end with timing.
        
        Usage:
            with logger.operation("detect_waste", item_id=123):
                # do work
                pass
        """
        start_time = time.time()
        self.info(f"Operation started: {operation_name}", operation=operation_name, **kwargs)
        
        try:
            yield
            duration = time.time() - start_time
            self.info(
                f"Operation completed: {operation_name}",
                operation=operation_name,
                duration_ms=round(duration * 1000, 2),
                status="success",
                **kwargs
            )
        except Exception as exc:
            duration = time.time() - start_time
            self.error(
                f"Operation failed: {operation_name}",
                error=exc,
                operation=operation_name,
                duration_ms=round(duration * 1000, 2),
                status="failed",
                **kwargs
            )
            raise


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add context if present
        if hasattr(record, "context"):
            log_data.update(record.context)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class PerformanceTracker:
    """Track and log performance metrics."""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.metrics: Dict[str, list[float]] = {}
    
    def record_timing(self, operation: str, duration_ms: float):
        """Record timing for an operation."""
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration_ms)
        
        # Keep only last 100 samples
        if len(self.metrics[operation]) > 100:
            self.metrics[operation] = self.metrics[operation][-100:]
    
    def get_stats(self, operation: str) -> Optional[Dict[str, float]]:
        """Get statistics for an operation."""
        if operation not in self.metrics or not self.metrics[operation]:
            return None
        
        timings = self.metrics[operation]
        return {
            "count": len(timings),
            "avg_ms": round(sum(timings) / len(timings), 2),
            "min_ms": round(min(timings), 2),
            "max_ms": round(max(timings), 2),
            "p95_ms": round(sorted(timings)[int(len(timings) * 0.95)], 2) if len(timings) >= 20 else None
        }
    
    def log_summary(self):
        """Log summary of all tracked operations."""
        summary = {op: self.get_stats(op) for op in self.metrics.keys()}
        self.logger.info("Performance summary", performance=summary)


def log_function(logger: StructuredLogger, level: int = logging.INFO):
    """
    Decorator to log function calls with timing.
    
    Usage:
        @log_function(logger)
        def my_function(arg1, arg2):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            start_time = time.time()
            
            logger.log(level, f"Calling {func_name}", function=func_name, args_count=len(args))
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.log(
                    level,
                    f"Completed {func_name}",
                    function=func_name,
                    duration_ms=round(duration * 1000, 2),
                    status="success"
                )
                return result
            except Exception as exc:
                duration = time.time() - start_time
                logger.error(
                    f"Failed {func_name}",
                    error=exc,
                    function=func_name,
                    duration_ms=round(duration * 1000, 2),
                    status="failed"
                )
                raise
        
        return wrapper
    return decorator


# Global logger instances
system_logger = StructuredLogger("waste_ai.system")
inference_logger = StructuredLogger("waste_ai.inference")
api_logger = StructuredLogger("waste_ai.api")
performance_tracker = PerformanceTracker(system_logger)
