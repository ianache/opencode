"""
MCP tools for incident management operations.

Provides MCP tools for creating and managing incidents
in Neo4j database through the ProductManager.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from fastmcp import Context
from loguru import logger

from graph.neo4j_client import create_neo4j_client
from graph.product_manager import ProductManager
from mcp_server.auth.middleware import AuthMiddleware
from mcp_server.models.requests import (
    IncidentRegistrationRequest,
)
from mcp_server.models.responses import (
    IncidentData,
    IncidentRegistrationResponse,
    SuccessResponse,
    ErrorResponse,
)


def serialize_datetime(dt_obj: Any) -> Any:
    """Convert datetime objects to ISO strings for JSON serialization."""
    # Handle None
    if dt_obj is None:
        return None

    # Handle neo4j.time.DateTime specifically
    if hasattr(dt_obj, "isoformat"):
        return dt_obj.isoformat()

    # Handle standard Python datetime
    if isinstance(dt_obj, datetime):
        return dt_obj.isoformat()

    # Handle lists recursively
    if isinstance(dt_obj, list):
        return [serialize_datetime(item) for item in dt_obj]

    # Handle dictionaries recursively
    if isinstance(dt_obj, dict):
        return {key: serialize_datetime(value) for key, value in dt_obj.items()}

    # Handle other types (including neo4j.time.DateTime)
    if hasattr(dt_obj, "year") and hasattr(dt_obj, "month") and hasattr(dt_obj, "day"):
        # Try to convert neo4j DateTime-like objects
        try:
            return str(dt_obj)
        except:
            return dt_obj.__str__() if hasattr(dt_obj, "__str__") else dt_obj

    return dt_obj


class IncidentTools:
    """MCP tools for incident management."""

    def __init__(self, auth_middleware=None):
        """Initialize incident tools with optional authentication.

        Args:
            auth_middleware: Authentication middleware instance
        """
        self.auth_middleware = auth_middleware or AuthMiddleware()
        self.neo4j_client = create_neo4j_client()
        self.product_manager = ProductManager(self.neo4j_client)

    def register_incident(
        self, ctx: Context, incident_data: IncidentRegistrationRequest
    ) -> Dict[str, Any]:
        """Register a new incident for a functionality.

        Args:
            ctx: MCP context
            incident_data: Incident registration data with all required fields
                         according to ontological model

        Returns:
            Incident registration response

        Raises:
            Exception: If registration fails or data is incomplete
        """
        try:
            logger.info(f"Registering incident: {incident_data.code}")

            # Validate that all required fields are present
            missing_fields = []
            if not incident_data.code:
                missing_fields.append("code")
            if not incident_data.description:
                missing_fields.append("description")
            if not incident_data.sla_level:
                missing_fields.append("sla_level")
            if not incident_data.functionality_code:
                missing_fields.append("functionality_code")

            if missing_fields:
                raise Exception("Datos incompletos proporcionados")

            # Validate that functionality exists
            functionality = self.product_manager.get_functionality(
                incident_data.functionality_code
            )
            if not functionality:
                raise Exception(
                    f"Functionality '{incident_data.functionality_code}' not found"
                )

            # Register the incident
            incident = self.product_manager.create_incident(
                code=incident_data.code,
                description=incident_data.description,
                sla_level=incident_data.sla_level,
                functionality_code=incident_data.functionality_code,
            )

            # Create response
            response = {
                "success": True,
                "message": f"Incident '{incident_data.code}' registered successfully",
                "incident": serialize_datetime(
                    {
                        "code": incident["code"],
                        "description": incident["description"],
                        "sla_level": incident["sla_level"],
                        "created_at": incident.get("created_at"),
                        "functionality_code": incident_data.functionality_code,
                    }
                ),
            }

            logger.info(f"Incident registered successfully: {incident_data.code}")
            return response

        except Exception as e:
            error_msg = str(e)

            # Handle specific error cases
            if "Datos incompletos proporcionados" in error_msg:
                logger.error(
                    f"Incomplete data provided for incident registration: {error_msg}"
                )
                raise Exception(error_msg)

            if "not found" in error_msg:
                logger.error(f"Functionality not found: {error_msg}")
                raise Exception(error_msg)

            # Handle duplicate incident codes
            if "already exists" in error_msg.lower() or "unique" in error_msg.lower():
                logger.error(
                    f"Incident with code '{incident_data.code}' already exists"
                )
                raise Exception(
                    f"Incident with code '{incident_data.code}' already exists"
                )

            logger.error(f"Failed to register incident: {error_msg}")
            raise Exception(f"Failed to register incident: {str(e)}")

    def get_incident_details(self, ctx: Context, incident_code: str) -> Dict[str, Any]:
        """Get detailed information about a specific incident.

        Args:
            ctx: MCP context
            incident_code: Incident unique identifier

        Returns:
            Incident details

        Raises:
            Exception: If incident is not found or access fails
        """
        try:
            logger.info(f"Getting incident details: {incident_code}")

            incident = self.product_manager.get_incident(incident_code)

            if not incident:
                raise Exception(f"Incident '{incident_code}' not found")

            response = {
                "success": True,
                "incident": serialize_datetime(
                    {
                        "code": incident["code"],
                        "description": incident["description"],
                        "sla_level": incident["sla_level"],
                        "created_at": incident.get("created_at"),
                    }
                ),
            }

            return response

        except Exception as e:
            logger.error(f"Failed to get incident details: {e}")
            raise Exception(f"Failed to retrieve incident details: {str(e)}")

    def list_incidents_by_functionality(
        self, ctx: Context, functionality_code: str, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """List all incidents for a specific functionality.

        Args:
            ctx: MCP context
            functionality_code: Functionality code
            limit: Maximum number of incidents to return
            offset: Number of incidents to skip

        Returns:
            List of incidents for the functionality

        Raises:
            Exception: If functionality is not found or access fails
        """
        try:
            logger.info(f"Listing incidents for functionality: {functionality_code}")

            # Validate functionality exists
            functionality = self.product_manager.get_functionality(functionality_code)
            if not functionality:
                raise Exception(f"Functionality '{functionality_code}' not found")

            # Get incidents
            incidents = self.product_manager.get_incidents_by_functionality(
                functionality_code
            )

            # Apply pagination
            total = len(incidents)
            paginated_incidents = incidents[offset : offset + limit]

            # Format response
            incident_list = [
                serialize_datetime(
                    {
                        "code": incident["i"]["code"],
                        "description": incident["i"]["description"],
                        "sla_level": incident["i"]["sla_level"],
                        "created_at": incident["i"].get("created_at"),
                    }
                )
                for incident in paginated_incidents
                if incident and incident.get("i")
            ]

            response = {
                "success": True,
                "functionality_code": functionality_code,
                "incidents": incident_list,
                "total": total,
                "limit": limit,
                "offset": offset,
            }

            return response

        except Exception as e:
            logger.error(f"Failed to list incidents for functionality: {e}")
            raise Exception(f"Failed to list incidents: {str(e)}")

    def list_incidents_by_product(
        self, ctx: Context, product_code: str, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """List all incidents for a specific product.

        Args:
            ctx: MCP context
            product_code: Product code
            limit: Maximum number of incidents to return
            offset: Number of incidents to skip

        Returns:
            List of incidents for the product

        Raises:
            Exception: If product is not found or access fails
        """
        try:
            logger.info(f"Listing incidents for product: {product_code}")

            # Validate product exists
            product = self.product_manager.get_product(product_code)
            if not product:
                raise Exception(f"Product '{product_code}' not found")

            # Get incidents
            incidents = self.product_manager.get_incidents_by_product(product_code)

            # Apply pagination
            total = len(incidents)
            paginated_incidents = incidents[offset : offset + limit]

            # Format response
            incident_list = [
                serialize_datetime(
                    {
                        "code": incident["i"]["code"],
                        "description": incident["i"]["description"],
                        "sla_level": incident["i"]["sla_level"],
                        "created_at": incident["i"].get("created_at"),
                        "functionality_code": incident.get("f", {}).get("code"),
                    }
                )
                for incident in paginated_incidents
                if incident and incident.get("i")
            ]

            response = {
                "success": True,
                "product_code": product_code,
                "incidents": incident_list,
                "total": total,
                "limit": limit,
                "offset": offset,
            }

            return response

        except Exception as e:
            logger.error(f"Failed to list incidents for product: {e}")
            raise Exception(f"Failed to list incidents: {str(e)}")
