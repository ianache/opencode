"""
MCP tools for functionality management operations.

Provides MCP tools for creating, reading, and assigning functionalities
in the Neo4j database through the ProductManager.
"""

from typing import Any, Dict, List, Optional

from fastmcp import Context, ToolError
from loguru import logger

from graph.neo4j_client import create_neo4j_client
from graph.product_manager import ProductManager
from mcp.models.requests import (
    FunctionalityRegistrationRequest,
    FunctionalityAssignmentRequest,
)
from mcp.models.responses import FunctionalityData, SuccessResponse


class FunctionalityTools:
    """MCP tools for functionality management."""

    def __init__(self, auth_middleware=None):
        """Initialize functionality tools with optional authentication.

        Args:
            auth_middleware: Authentication middleware instance
        """
        self.auth_middleware = auth_middleware
        self._product_manager: Optional[ProductManager] = None

    @property
    def product_manager(self) -> ProductManager:
        """Lazy initialization of ProductManager."""
        if self._product_manager is None:
            neo4j_client = create_neo4j_client()
            neo4j_client.connect()
            self._product_manager = ProductManager(neo4j_client)
        return self._product_manager

    def register_functionality(
        self, ctx: Context, code: str, name: str
    ) -> Dict[str, Any]:
        """Register a new functionality.

        Args:
            ctx: MCP context
            code: Functionality unique identifier (required)
            name: Functionality descriptive name (required)

        Returns:
            Functionality registration result

        Raises:
            ToolError: If validation fails or functionality creation fails
        """
        try:
            # Validate input
            request = FunctionalityRegistrationRequest(code=code, name=name)

            logger.info(f"Registering functionality: {request.code}")

            # Create functionality
            functionality_node = self.product_manager.create_functionality(
                request.code, request.name
            )

            response = {
                "success": True,
                "message": f"Functionality '{request.code}' registered successfully",
                "functionality": {
                    "code": functionality_node["code"],
                    "name": functionality_node["name"],
                    "created_at": functionality_node.get("created_at"),
                },
            }

            logger.info(f"Functionality registered: {request.code}")
            return response

        except ValueError as e:
            logger.error(f"Functionality registration validation error: {e}")
            raise ToolError(f"Validation error: {str(e)}")

        except Exception as e:
            logger.error(f"Functionality registration failed: {e}")
            raise ToolError(f"Failed to register functionality: {str(e)}")

    def get_functionality_details(
        self, ctx: Context, functionality_code: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific functionality.

        Args:
            ctx: MCP context
            functionality_code: Functionality unique identifier

        Returns:
            Functionality details with products and components

        Raises:
            ToolError: If functionality is not found or access fails
        """
        try:
            logger.info(f"Getting functionality details: {functionality_code}")

            functionality_details = (
                self.product_manager.get_functionality_with_products(functionality_code)
            )

            if not functionality_details or not functionality_details.get("f"):
                raise ToolError(f"Functionality '{functionality_code}' not found")

            functionality = functionality_details["f"]
            products = functionality_details.get("products", [])
            components = functionality_details.get("components", [])
            incidents = functionality_details.get("incidents", [])
            resolutions = functionality_details.get("resolutions", [])

            response = {
                "success": True,
                "functionality": {
                    "code": functionality["code"],
                    "name": functionality["name"],
                    "created_at": functionality.get("created_at"),
                },
                "products": [
                    {
                        "code": prod["code"],
                        "name": prod["name"],
                        "created_at": prod.get("created_at"),
                    }
                    for prod in products
                ],
                "components": [
                    {
                        "code": comp["code"],
                        "name": comp["name"],
                        "created_at": comp.get("created_at"),
                    }
                    for comp in components
                ],
                "incident_count": len(incidents),
                "incidents": [
                    {
                        "code": inc["code"],
                        "description": inc["description"],
                        "sla_level": inc["sla_level"],
                        "created_at": inc.get("created_at"),
                    }
                    for inc in incidents
                ],
                "resolution_count": len(resolutions),
                "resolutions": [
                    {
                        "incident_code": res["incident_code"],
                        "procedure": res["procedure"],
                        "resolution_date": res.get("resolution_date"),
                        "created_at": res.get("created_at"),
                    }
                    for res in resolutions
                ],
            }

            logger.info(f"Retrieved functionality details: {functionality_code}")
            return response

        except ToolError:
            raise

        except Exception as e:
            logger.error(f"Failed to get functionality details: {e}")
            raise ToolError(f"Failed to retrieve functionality details: {str(e)}")

    def assign_functionalities_to_product(
        self, ctx: Context, product_code: str, functionality_codes: List[str]
    ) -> Dict[str, Any]:
        """Assign multiple functionalities to a product.

        Args:
            ctx: MCP context
            product_code: Product unique identifier
            functionality_codes: List of functionality codes to assign

        Returns:
            Assignment result

        Raises:
            ToolError: If assignment fails
        """
        try:
            # Validate input
            request = FunctionalityAssignmentRequest(
                product_code=product_code, functionality_codes=functionality_codes
            )

            logger.info(
                f"Assigning {len(request.functionality_codes)} functionalities to product: {request.product_code}"
            )

            # Check if product exists
            product = self.product_manager.get_product(request.product_code)
            if not product:
                raise ToolError(f"Product '{request.product_code}' not found")

            # Assign functionalities
            successful_assignments = []
            failed_assignments = []

            for func_code in request.functionality_codes:
                try:
                    # Ensure functionality exists
                    func = self.product_manager.get_functionality(func_code)
                    if not func:
                        failed_assignments.append(
                            {
                                "functionality_code": func_code,
                                "error": "Functionality not found",
                            }
                        )
                        continue

                    # Assign functionality to product
                    success = self.product_manager.assign_functionality_to_product(
                        request.product_code, func_code
                    )

                    if success:
                        successful_assignments.append(
                            {
                                "functionality_code": func_code,
                                "functionality_name": func["name"],
                            }
                        )
                    else:
                        failed_assignments.append(
                            {
                                "functionality_code": func_code,
                                "error": "Assignment failed",
                            }
                        )

                except Exception as e:
                    failed_assignments.append(
                        {"functionality_code": func_code, "error": str(e)}
                    )

            response = {
                "success": len(successful_assignments) > 0,
                "message": f"Assigned {len(successful_assignments)} of {len(request.functionality_codes)} functionalities",
                "product_code": request.product_code,
                "successful_assignments": successful_assignments,
                "failed_assignments": failed_assignments,
                "summary": {
                    "total_requested": len(request.functionality_codes),
                    "successful": len(successful_assignments),
                    "failed": len(failed_assignments),
                },
            }

            logger.info(
                f"Functionality assignment completed: {len(successful_assignments)} successful, {len(failed_assignments)} failed"
            )
            return response

        except ValueError as e:
            logger.error(f"Functionality assignment validation error: {e}")
            raise ToolError(f"Validation error: {str(e)}")

        except Exception as e:
            logger.error(f"Functionality assignment failed: {e}")
            raise ToolError(f"Failed to assign functionalities: {str(e)}")

    def remove_functionalities_from_product(
        self, ctx: Context, product_code: str, functionality_codes: List[str]
    ) -> Dict[str, Any]:
        """Remove multiple functionalities from a product.

        Args:
            ctx: MCP context
            product_code: Product unique identifier
            functionality_codes: List of functionality codes to remove

        Returns:
            Removal result

        Raises:
            ToolError: If removal fails
        """
        try:
            if not functionality_codes:
                raise ToolError("At least one functionality code must be provided")

            logger.info(
                f"Removing {len(functionality_codes)} functionalities from product: {product_code}"
            )

            # Check if product exists
            product = self.product_manager.get_product(product_code)
            if not product:
                raise ToolError(f"Product '{product_code}' not found")

            # Remove functionalities
            successful_removals = []
            failed_removals = []

            for func_code in functionality_codes:
                try:
                    success = self.product_manager.remove_functionality_from_product(
                        product_code, func_code
                    )

                    if success:
                        successful_removals.append({"functionality_code": func_code})
                    else:
                        failed_removals.append(
                            {
                                "functionality_code": func_code,
                                "error": "Removal failed - functionality may not be assigned",
                            }
                        )

                except Exception as e:
                    failed_removals.append(
                        {"functionality_code": func_code, "error": str(e)}
                    )

            response = {
                "success": len(successful_removals) > 0,
                "message": f"Removed {len(successful_removals)} of {len(functionality_codes)} functionalities",
                "product_code": product_code,
                "successful_removals": successful_removals,
                "failed_removals": failed_removals,
                "summary": {
                    "total_requested": len(functionality_codes),
                    "successful": len(successful_removals),
                    "failed": len(failed_removals),
                },
            }

            logger.info(
                f"Functionality removal completed: {len(successful_removals)} successful, {len(failed_removals)} failed"
            )
            return response

        except ToolError:
            raise

        except Exception as e:
            logger.error(f"Functionality removal failed: {e}")
            raise ToolError(f"Failed to remove functionalities: {str(e)}")

    def list_functionalities(
        self, ctx: Context, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """List all functionalities with pagination.

        Args:
            ctx: MCP context
            limit: Maximum number of functionalities to return (default: 50, max: 1000)
            offset: Number of functionalities to skip (default: 0)

        Returns:
            Paginated list of functionalities

        Raises:
            ToolError: If listing fails
        """
        try:
            # Validate pagination parameters
            if not (1 <= limit <= 1000):
                raise ToolError("Limit must be between 1 and 1000")
            if offset < 0:
                raise ToolError("Offset must be non-negative")

            logger.info(f"Listing functionalities: limit={limit}, offset={offset}")

            # Get all functionalities through products query
            # Since ProductManager doesn't have direct list_functionalities,
            # we'll get them from product relationships
            products_summary = self.product_manager.get_all_products_summary()

            # Collect unique functionalities from all products
            all_functionalities = set()
            functionality_details = {}

            for product_summary in products_summary:
                # This is a simplified approach - in production,
                # we might need a dedicated query
                pass

            # For now, return a simple response structure
            # This would need to be enhanced with actual functionality listing
            response = {
                "success": True,
                "functionalities": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "note": "Functionality listing requires enhanced ProductManager implementation",
            }

            logger.info("Functionality listing completed")
            return response

        except ToolError:
            raise

        except Exception as e:
            logger.error(f"Failed to list functionalities: {e}")
            raise ToolError(f"Failed to list functionalities: {str(e)}")
