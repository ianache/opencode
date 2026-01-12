"""
Custom exceptions for GraphRAG application.

Provides specific exception types for different error scenarios
to enable better error handling and debugging.
"""

from typing import Any, Optional


class GraphRAGError(Exception):
    """Base exception for all GraphRAG application errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details


class ConfigurationError(GraphRAGError):
    """Exception raised for configuration-related errors."""

    def __init__(self, message: str, missing_vars: Optional[list] = None):
        super().__init__(message, error_code="CONFIG_ERROR", details=missing_vars)
        self.missing_vars = missing_vars or []


class DatabaseConnectionError(GraphRAGError):
    """Exception raised for database connection errors."""

    def __init__(self, message: str, connection_params: Optional[dict] = None):
        super().__init__(
            message, error_code="DB_CONNECTION_ERROR", details=connection_params
        )
        self.connection_params = connection_params or {}


class DatabaseQueryError(GraphRAGError):
    """Exception raised for database query errors."""

    def __init__(
        self, message: str, query: Optional[str] = None, params: Optional[dict] = None
    ):
        super().__init__(
            message,
            error_code="DB_QUERY_ERROR",
            details={"query": query, "params": params},
        )
        self.query = query
        self.params = params or {}


class DataProcessingError(GraphRAGError):
    """Exception raised for data processing errors."""

    def __init__(self, message: str, data_info: Optional[dict] = None):
        super().__init__(message, error_code="DATA_PROCESSING_ERROR", details=data_info)
        self.data_info = data_info or {}


class DataValidationError(GraphRAGError):
    """Exception raised for data validation errors."""

    def __init__(self, message: str, validation_errors: Optional[list] = None):
        super().__init__(
            message, error_code="DATA_VALIDATION_ERROR", details=validation_errors
        )
        self.validation_errors = validation_errors or []


class PerformanceError(GraphRAGError):
    """Exception raised for performance-related errors."""

    def __init__(self, message: str, metrics: Optional[dict] = None):
        super().__init__(message, error_code="PERFORMANCE_ERROR", details=metrics)
        self.metrics = metrics or {}


class ExternalServiceError(GraphRAGError):
    """Exception raised for external service errors (e.g., API calls, file downloads)."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        super().__init__(
            message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service_name, "status_code": status_code},
        )
        self.service_name = service_name
        self.status_code = status_code
