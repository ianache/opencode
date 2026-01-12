"""
Performance monitoring utilities for GraphRAG application.

Provides timing, metrics collection, and performance
analysis functionality.
"""

import functools
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from utils.logging import get_logger


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""

    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Performance monitoring utility."""

    def __init__(self):
        self.logger = get_logger("performance")
        self.metrics: Dict[str, PerformanceMetrics] = {}

    def time_operation(self, operation_name: str) -> Callable:
        """Decorator to time operations."""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Start timing
                start_time = time.time()
                metrics = PerformanceMetrics(
                    operation_name=operation_name, start_time=start_time
                )

                try:
                    # Execute operation
                    result = func(*args, **kwargs)

                    # Record success
                    end_time = time.time()
                    metrics.end_time = end_time
                    metrics.duration = end_time - start_time
                    metrics.success = True

                    self.metrics[operation_name] = metrics
                    self.logger.info(
                        f"Operation '{operation_name}' completed in {metrics.duration:.3f}s"
                    )

                    return result

                except Exception as e:
                    # Record failure
                    end_time = time.time()
                    metrics.end_time = end_time
                    metrics.duration = end_time - start_time
                    metrics.success = False
                    metrics.error_message = str(e)

                    self.metrics[operation_name] = metrics
                    self.logger.error(
                        f"Operation '{operation_name}' failed after {metrics.duration:.3f}s: {e}"
                    )

                    raise

            return wrapper

        return decorator

    def record_metric(
        self,
        operation_name: str,
        duration: float,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Manually record a performance metric."""
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time() - duration,
            end_time=time.time(),
            duration=duration,
            success=success,
            error_message=error_message,
            metadata=metadata or {},
        )

        self.metrics[operation_name] = metrics

        if success:
            self.logger.info(f"Operation '{operation_name}' recorded: {duration:.3f}s")
        else:
            self.logger.error(
                f"Operation '{operation_name}' failed after {duration:.3f}s: {error_message}"
            )

    def get_metrics(
        self, operation_name: Optional[str] = None
    ) -> Dict[str, PerformanceMetrics]:
        """Get performance metrics."""
        if operation_name:
            return {operation_name: self.metrics.get(operation_name)}
        return self.metrics.copy()

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.metrics:
            return {"total_operations": 0}

        successful_ops = [m for m in self.metrics.values() if m.success]
        failed_ops = [m for m in self.metrics.values() if not m.success]

        durations = [
            m.duration for m in self.metrics.values() if m.duration is not None
        ]

        summary = {
            "total_operations": len(self.metrics),
            "successful_operations": len(successful_ops),
            "failed_operations": len(failed_ops),
            "success_rate": (
                len(successful_ops) / len(self.metrics) if self.metrics else 0
            ),
        }

        if durations:
            summary.update(
                {
                    "average_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "total_duration": sum(durations),
                }
            )

        return summary

    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        self.metrics.clear()
        self.logger.info("Performance metrics cleared")

    def export_metrics(self) -> str:
        """Export metrics as formatted string."""
        summary = self.get_summary()

        output = [
            "=== Performance Metrics Summary ===",
            f"Total Operations: {summary['total_operations']}",
            f"Successful: {summary['successful_operations']}",
            f"Failed: {summary['failed_operations']}",
            f"Success Rate: {summary['success_rate']:.2%}",
        ]

        if "average_duration" in summary:
            output.extend(
                [
                    f"Average Duration: {summary['average_duration']:.3f}s",
                    f"Min Duration: {summary['min_duration']:.3f}s",
                    f"Max Duration: {summary['max_duration']:.3f}s",
                    f"Total Duration: {summary['total_duration']:.3f}s",
                ]
            )

        return "\n".join(output)


# Global performance monitor instance
_performance_monitor = Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def monitor_performance(operation_name: str) -> Callable:
    """Decorator to monitor function performance."""
    monitor = get_performance_monitor()
    return monitor.time_operation(operation_name)


# Performance monitoring context manager
class OperationTimer:
    """Context manager for timing operations."""

    def __init__(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        self.operation_name = operation_name
        self.metadata = metadata
        self.monitor = get_performance_monitor()
        self.start_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is None:
            return

        duration = time.time() - self.start_time
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None

        self.monitor.record_metric(
            operation_name=self.operation_name,
            duration=duration,
            success=success,
            error_message=error_message,
            metadata=self.metadata,
        )
