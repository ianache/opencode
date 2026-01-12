"""
Pydantic models for MCP requests and responses.

Provides data validation and serialization for all MCP operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProductRegistrationRequest(BaseModel):
    """Request model for product registration."""

    code: str = Field(
        ..., min_length=1, max_length=20, description="Product unique identifier"
    )
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    functionalities: Optional[List[str]] = Field(
        default=[], description="List of functionality codes to assign"
    )


class FunctionalityRegistrationRequest(BaseModel):
    """Request model for functionality registration."""

    code: str = Field(
        ..., min_length=1, max_length=20, description="Functionality unique identifier"
    )
    name: str = Field(
        ..., min_length=1, max_length=200, description="Functionality name"
    )


class FunctionalityAssignmentRequest(BaseModel):
    """Request model for functionality assignment to products."""

    product_code: str = Field(..., description="Product code")
    functionality_codes: List[str] = Field(
        ..., min_items=1, description="List of functionality codes"
    )


class ProductUpdateRequest(BaseModel):
    """Request model for product updates."""

    code: str = Field(..., description="Product code to update")
    name: Optional[str] = Field(
        None, min_length=1, max_length=200, description="New product name"
    )
    # Add other updatable fields as needed


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
