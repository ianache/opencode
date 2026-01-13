"""
Pydantic models for MCP requests.

Provides data validation and serialization for all MCP request operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


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
        ..., description="List of functionality codes"
    )

    @validator("functionality_codes")
    def validate_functionality_codes(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one functionality code must be provided")
        return v


class IncidentRegistrationRequest(BaseModel):
    """Request model for incident registration."""

    code: str = Field(
        ..., min_length=1, max_length=20, description="Incident unique identifier"
    )
    description: str = Field(
        ..., min_length=1, max_length=500, description="Incident description"
    )
    sla_level: str = Field(..., description="SLA priority level")
    functionality_code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Functionality code where incident occurred",
    )

    @validator("sla_level")
    def validate_sla_level(cls, v):
        valid_sla_levels = ["SLA_CRITICAL", "SLA_HIGH", "SLA_MEDIUM", "SLA_LOW"]
        if v not in valid_sla_levels:
            raise ValueError(f"SLA level must be one of: {', '.join(valid_sla_levels)}")
        return v


class ProductUpdateRequest(BaseModel):
    """Request model for product updates."""

    code: str = Field(..., description="Product code to update")
    name: Optional[str] = Field(
        None, min_length=1, max_length=200, description="New product name"
    )
    # Add other updatable fields as needed


class PaginationParams(BaseModel):
    """Pagination parameters for list operations."""

    limit: int = Field(default=50, ge=1, le=1000, description="Maximum items to return")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
