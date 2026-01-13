"""
Pydantic models for MCP responses.

Provides data validation and serialization for all MCP response operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProductData(BaseModel):
    """Product data model."""

    code: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class FunctionalityData(BaseModel):
    """Functionality data model."""

    code: str
    name: str
    created_at: datetime


class IncidentData(BaseModel):
    """Incident data model."""

    code: str
    description: str
    sla_level: str
    created_at: datetime
    functionality_code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )


class SuccessResponse(BaseModel):
    """Standard success response model."""

    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class IncidentRegistrationResponse(BaseModel):
    """Response model for incident registration."""

    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Registration success message")
    incident: IncidentData


class PaginationParams(BaseModel):
    """Pagination parameters for list operations."""

    limit: int = Field(default=50, ge=1, le=1000, description="Maximum items to return")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class ProductListResponse(BaseModel):
    """Response model for product lists with pagination."""

    products: List[ProductData]
    total: int = Field(..., description="Total number of products")
    limit: int
    offset: int


class ProductDetailsResponse(BaseModel):
    """Detailed product response with functionalities."""

    product: ProductData
    functionalities: List[FunctionalityData]
    incident_count: int = Field(default=0, description="Number of incidents")
    resolution_count: int = Field(default=0, description="Number of resolutions")
