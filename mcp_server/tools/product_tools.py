"""
MCP tools for product management operations.

Provides MCP tools for creating, reading, updating, and deleting products
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
    ProductRegistrationRequest,
    ProductUpdateRequest,
    PaginationParams,
)
from mcp_server.models.responses import (
    ProductData,
    ProductListResponse,
    ProductDetailsResponse,
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


class ProductTools:
    """MCP tools for product management."""

    def __init__(self, auth_middleware: AuthMiddleware):
        """Initialize ProductTools with authentication middleware."""
        self.auth_middleware = auth_middleware
        self._product_manager = ProductManager(create_neo4j_client())

    def register_product(
        self,
        ctx: Context,
        code: str,
        name: str,
        functionalities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Register a new product with optional functionalities.

        Args:
            ctx: MCP context
            code: Product unique identifier
            name: Product name
            functionalities: Optional list of functionality codes to assign

        Returns:
            Registration result

        Raises:
            Exception: If registration fails
        """
        try:
            logger.info(f"Registering product: {code}")

            # Validate input
            request = ProductRegistrationRequest(
                code=code, name=name, functionalities=functionalities or []
            )

            # Create product
            product_node = self._product_manager.create_product(
                request.code, request.name
            )

            # Assign functionalities if provided
            assigned_functionalities = []
            if request.functionalities:
                for func_code in request.functionalities:
                    try:
                        success = self._product_manager.assign_functionality_to_product(
                            request.code, func_code
                        )
                        if success:
                            func = self._product_manager.get_functionality(func_code)
                            if func:
                                assigned_functionalities.append(
                                    {
                                        "code": func["code"],
                                        "name": func["name"],
                                        "created_at": func.get("created_at"),
                                    }
                                )
                    except Exception as e:
                        logger.warning(
                            f"Failed to assign functionality {func_code}: {e}"
                        )

            # Get created product with details
            product_details = self._product_manager.get_product_with_functionalities(
                request.code
            )

            response = {
                "success": True,
                "message": f"Product '{code}' registered successfully",
                "product": serialize_datetime(
                    {
                        "code": product_details["p"]["code"],
                        "name": product_details["p"]["name"],
                        "created_at": product_details["p"].get("created_at"),
                        "updated_at": product_details["p"].get("updated_at"),
                        "functionality_count": len(assigned_functionalities),
                        "functionalities": assigned_functionalities,
                    }
                ),
            }

            logger.info(f"Product registered: {code}")
            return response

        except ValueError as e:
            logger.error(f"Product registration validation error: {e}")
            raise Exception(f"Validation error: {str(e)}")

        except Exception as e:
            logger.error(f"Product registration failed: {e}")
            raise Exception(f"Failed to register product: {str(e)}")

    def get_product_details(self, ctx: Context, code: str) -> Dict[str, Any]:
        """Get detailed information about a specific product.

        Args:
            ctx: MCP context
            code: Product unique identifier

        Returns:
            Product details

        Raises:
            Exception: If product not found or access fails
        """
        try:
            logger.info(f"Getting product details: {code}")

            product_details = self._product_manager.get_product_with_functionalities(
                code
            )

            if not product_details or not product_details.get("p"):
                raise Exception(f"Product '{code}' not found")

            product = product_details["p"]
            functionalities = product_details.get("functionalities", [])
            incidents = product_details.get("incidents", [])
            resolutions = product_details.get("resolutions", [])

            response = {
                "success": True,
                "product": serialize_datetime(
                    {
                        "code": product["code"],
                        "name": product["name"],
                        "created_at": product.get("created_at"),
                        "updated_at": product.get("updated_at"),
                    }
                ),
                "functionalities": [
                    serialize_datetime(
                        {
                            "code": func["code"],
                            "name": func["name"],
                            "created_at": func.get("created_at"),
                        }
                    )
                    for func in functionalities
                    if func
                ],
                "incident_count": len(incidents),
                "incidents": [
                    serialize_datetime(
                        {
                            "code": inc["code"],
                            "description": inc["description"],
                            "sla_level": inc["sla_level"],
                            "created_at": inc.get("created_at"),
                        }
                    )
                    for inc in incidents
                    if inc
                ],
                "resolution_count": len(resolutions),
                "resolutions": [
                    serialize_datetime(
                        {
                            "incident_code": res["incident_code"],
                            "procedure": res["procedure"],
                            "resolution_date": res.get("resolution_date"),
                            "created_at": res.get("created_at"),
                        }
                    )
                    for res in resolutions
                ],
            }

            logger.info(f"Retrieved product details: {code}")
            return response

        except Exception as e:
            logger.error(f"Failed to get product details: {e}")
            raise Exception(f"Failed to retrieve product details: {str(e)}")

    def update_product(
        self, ctx: Context, product_code: str, name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update product information.

        Args:
            ctx: MCP context
            product_code: Product unique identifier
            name: New product name (optional)

        Returns:
            Update result

        Raises:
            Exception: If update fails or product not found
        """
        try:
            logger.info(f"Updating product: {product_code}")

            # Check if product exists
            existing = self._product_manager.get_product(product_code)
            if not existing:
                raise Exception(f"Product '{product_code}' not found")

            # Prepare updates
            updates = {}
            if name and name.strip():
                updates["name"] = name.strip()

            if not updates:
                raise Exception("No updates provided")

            # Update product
            success = self._product_manager.update_product(product_code, **updates)

            if success:
                # Get updated product
                updated = self._product_manager.get_product(product_code)

                if not updated:
                    raise Exception(f"Product '{product_code}' not found after update")

                response = {
                    "success": True,
                    "message": f"Product '{product_code}' updated successfully",
                    "product": serialize_datetime(
                        {
                            "code": updated["code"],
                            "name": updated["name"],
                            "updated_at": updated.get("updated_at"),
                        }
                    ),
                }

                logger.info(f"Product updated: {product_code}")
                return response
            else:
                raise Exception(f"Failed to update product '{product_code}'")

        except Exception as e:
            logger.error(f"Product update failed: {e}")
            raise Exception(f"Failed to update product: {str(e)}")

    def delete_product(self, ctx: Context, product_code: str) -> Dict[str, Any]:
        """Delete a product and all its relationships.

        Args:
            ctx: MCP context
            product_code: Product unique identifier

        Returns:
            Deletion result

        Raises:
            Exception: If deletion fails
        """
        try:
            logger.info(f"Deleting product: {product_code}")

            # Check if product exists
            existing = self._product_manager.get_product(product_code)
            if not existing:
                raise Exception(f"Product '{product_code}' not found")

            # Delete product
            success = self._product_manager.delete_product(product_code)

            if success:
                response = {
                    "success": True,
                    "message": f"Product '{product_code}' deleted successfully",
                    "deleted_product": serialize_datetime(
                        {
                            "code": existing["code"],
                            "name": existing["name"],
                        }
                    ),
                }

                logger.info(f"Product deleted: {product_code}")
                return response
            else:
                raise Exception(f"Failed to delete product '{product_code}'")

        except Exception as e:
            logger.error(f"Product deletion failed: {e}")
            raise Exception(f"Failed to delete product: {str(e)}")

    def list_products(
        self, ctx: Context, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """List all products with pagination.

        Args:
            ctx: MCP context
            limit: Maximum number of products to return (default: 50, max: 1000)
            offset: Number of products to skip (default: 0)

        Returns:
            Paginated list of products

        Raises:
            Exception: If listing fails
        """
        try:
            # Validate pagination parameters
            pagination = PaginationParams(limit=limit, offset=offset)

            logger.info(
                f"Listing products: limit={pagination.limit}, offset={pagination.offset}"
            )

            # Get all products
            all_products = self._product_manager.list_all_products()

            # Apply pagination
            total = len(all_products)
            paginated_products = all_products[
                pagination.offset : pagination.offset + pagination.limit
            ]

            # Format response
            product_list = [
                serialize_datetime(
                    {
                        "code": product["code"],
                        "name": product["name"],
                        "created_at": product.get("created_at"),
                    }
                )
                for product in paginated_products
                if product
            ]

            response = {
                "success": True,
                "products": product_list,
                "total": total,
                "limit": pagination.limit,
                "offset": pagination.offset,
            }

            logger.info(f"Listed {len(product_list)} products")
            return response

        except Exception as e:
            logger.error(f"Product listing failed: {e}")
            raise Exception(f"Failed to list products: {str(e)}")

    def search_products(
        self, ctx: Context, query: str, limit: int = 50
    ) -> Dict[str, Any]:
        """Search products by code or name with fuzzy matching.

        Args:
            ctx: MCP context
            query: Search query string
            limit: Maximum results to return (default: 50)

        Returns:
            Search results

        Raises:
            Exception: If search fails
        """
        try:
            logger.info(f"Searching products: query='{query}', limit={limit}")

            if not query or not query.strip():
                raise Exception("Search query cannot be empty")

            # Search products
            results = self._product_manager.search_products(query.strip(), limit)

            # Format response
            product_list = [
                serialize_datetime(
                    {
                        "code": product["code"],
                        "name": product["name"],
                        "created_at": product.get("created_at"),
                    }
                )
                for product in results
                if product
            ]

            response = {
                "success": True,
                "query": query,
                "products": product_list,
                "total": len(product_list),
                "limit": limit,
            }

            logger.info(f"Product search completed: {len(product_list)} results")
            return response

        except Exception as e:
            logger.error(f"Product search failed: {e}")
            raise Exception(f"Failed to search products: {str(e)}")
