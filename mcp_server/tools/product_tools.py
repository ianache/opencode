"""
MCP tools for product management operations.

Provides MCP tools for creating, reading, updating, and deleting products
in the Neo4j database through the ProductManager.
"""

from typing import Any, Dict, List, Optional

from fastmcp import Context, ToolError
from loguru import logger

from graph.neo4j_client import create_neo4j_client
from graph.product_manager import ProductManager
from mcp.auth.middleware import AuthMiddleware
from mcp.models.requests import (
    ProductRegistrationRequest,
    ProductUpdateRequest,
    PaginationParams,
)
from mcp.models.responses import (
    ProductData,
    ProductListResponse,
    SuccessResponse,
    ErrorResponse,
)
from mcp.models.responses import (
    ProductResponse,
    ProductListResponse,
    SuccessResponse,
    ErrorResponse,
)


class ProductTools:
    """MCP tools for product management."""

    def __init__(self, auth_middleware: Optional[AuthMiddleware] = None):
        """Initialize product tools with optional authentication.

        Args:
            auth_middleware: Authentication middleware instance
        """
        self.auth_middleware = auth_middleware or AuthMiddleware()
        self._product_manager: Optional[ProductManager] = None

    @property
    def product_manager(self) -> ProductManager:
        """Lazy initialization of ProductManager."""
        if self._product_manager is None:
            neo4j_client = create_neo4j_client()
            neo4j_client.connect()
            self._product_manager = ProductManager(neo4j_client)
        return self._product_manager

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
            code: Product unique identifier (required)
            name: Product descriptive name (required)
            functionalities: List of functionality codes to assign (optional)

        Returns:
            Product registration result

        Raises:
            ToolError: If validation fails or product creation fails
        """
        try:
            # Validate input
            request = ProductRegistrationRequest(
                code=code, name=name, functionalities=functionalities or []
            )

            logger.info(f"Registering product: {request.code}")

            # Create product
            product_node = self.product_manager.create_product(
                request.code, request.name
            )

            # Assign functionalities if provided
            assigned_functionalities = []
            if request.functionalities:
                for func_code in request.functionalities:
                    try:
                        # Ensure functionality exists
                        func = self.product_manager.get_functionality(func_code)
                        if not func:
                            raise ToolError(f"Functionality '{func_code}' not found")

                        # Assign functionality to product
                        success = self.product_manager.assign_functionality_to_product(
                            request.code, func_code
                        )
                        if success:
                            assigned_functionalities.append(func_code)

                    except Exception as e:
                        logger.warning(
                            f"Failed to assign functionality {func_code}: {e}"
                        )

            # Get complete product details
            product_details = self.product_manager.get_product_with_functionalities(
                request.code
            )

            response = {
                "success": True,
                "message": f"Product '{request.code}' registered successfully",
                "product": {
                    "code": product_node["code"],
                    "name": product_node["name"],
                    "created_at": product_node.get("created_at"),
                    "functionalities": assigned_functionalities,
                    "functionality_count": len(assigned_functionalities),
                },
            }

            logger.info(
                f"Product registered: {request.code} with {len(assigned_functionalities)} functionalities"
            )
            return response

        except ValueError as e:
            logger.error(f"Product registration validation error: {e}")
            raise ToolError(f"Validation error: {str(e)}")

        except Exception as e:
            logger.error(f"Product registration failed: {e}")
            raise ToolError(f"Failed to register product: {str(e)}")

    def get_product_details(self, ctx: Context, product_code: str) -> Dict[str, Any]:
        """Get detailed information about a specific product.

        Args:
            ctx: MCP context
            product_code: Product unique identifier

        Returns:
            Product details with functionalities and incidents

        Raises:
            ToolError: If product is not found or access fails
        """
        try:
            logger.info(f"Getting product details: {product_code}")

            product_details = self.product_manager.get_product_with_functionalities(
                product_code
            )

            if not product_details or not product_details.get("p"):
                raise ToolError(f"Product '{product_code}' not found")

            product = product_details["p"]
            functionalities = product_details.get("functionalities", [])
            incidents = product_details.get("incidents", [])
            resolutions = product_details.get("resolutions", [])

            response = {
                "success": True,
                "product": {
                    "code": product["code"],
                    "name": product["name"],
                    "created_at": product.get("created_at"),
                    "updated_at": product.get("updated_at"),
                },
                "functionalities": [
                    {
                        "code": func["code"],
                        "name": func["name"],
                        "created_at": func.get("created_at"),
                    }
                    for func in functionalities
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

            logger.info(f"Retrieved product details: {product_code}")
            return response

        except ToolError:
            raise

        except Exception as e:
            logger.error(f"Failed to get product details: {e}")
            raise ToolError(f"Failed to retrieve product details: {str(e)}")

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
            ToolError: If update fails or product not found
        """
        try:
            logger.info(f"Updating product: {product_code}")

            # Check if product exists
            existing = self.product_manager.get_product(product_code)
            if not existing:
                raise ToolError(f"Product '{product_code}' not found")

            # Prepare updates
            updates = {}
            if name and name.strip():
                updates["name"] = name.strip()

            if not updates:
                raise ToolError("No updates provided")

            # Update product
            success = self.product_manager.update_product(product_code, **updates)

            if success:
                # Get updated product
                updated = self.product_manager.get_product(product_code)

                response = {
                    "success": True,
                    "message": f"Product '{product_code}' updated successfully",
                    "product": {
                        "code": updated["code"],
                        "name": updated["name"],
                        "updated_at": updated.get("updated_at"),
                    },
                }

                logger.info(f"Product updated: {product_code}")
                return response
            else:
                raise ToolError(f"Failed to update product '{product_code}'")

        except ToolError:
            raise

        except Exception as e:
            logger.error(f"Product update failed: {e}")
            raise ToolError(f"Failed to update product: {str(e)}")

    def delete_product(self, ctx: Context, product_code: str) -> Dict[str, Any]:
        """Delete a product and all its relationships.

        Args:
            ctx: MCP context
            product_code: Product unique identifier

        Returns:
            Deletion result

        Raises:
            ToolError: If deletion fails
        """
        try:
            logger.info(f"Deleting product: {product_code}")

            # Check if product exists
            existing = self.product_manager.get_product(product_code)
            if not existing:
                raise ToolError(f"Product '{product_code}' not found")

            # Delete product
            success = self.product_manager.delete_product(product_code)

            if success:
                response = {
                    "success": True,
                    "message": f"Product '{product_code}' deleted successfully",
                    "deleted_product": {
                        "code": existing["code"],
                        "name": existing["name"],
                    },
                }

                logger.info(f"Product deleted: {product_code}")
                return response
            else:
                raise ToolError(f"Failed to delete product '{product_code}'")

        except ToolError:
            raise

        except Exception as e:
            logger.error(f"Product deletion failed: {e}")
            raise ToolError(f"Failed to delete product: {str(e)}")

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
            ToolError: If listing fails
        """
        try:
            # Validate pagination parameters
            pagination = PaginationParams(limit=limit, offset=offset)

            logger.info(
                f"Listing products: limit={pagination.limit}, offset={pagination.offset}"
            )

            # Get all products
            all_products = self.product_manager.list_all_products()

            # Apply pagination
            total = len(all_products)
            paginated_products = all_products[
                pagination.offset : pagination.offset + pagination.limit
            ]

            # Format response
            product_list = [
                {
                    "code": product["code"],
                    "name": product["name"],
                    "created_at": product.get("created_at"),
                }
                for product in paginated_products
            ]

            response = {
                "success": True,
                "products": product_list,
                "total": total,
                "limit": pagination.limit,
                "offset": pagination.offset,
                "has_more": pagination.offset + pagination.limit < total,
            }

            logger.info(f"Retrieved {len(product_list)} products")
            return response

        except Exception as e:
            logger.error(f"Failed to list products: {e}")
            raise ToolError(f"Failed to list products: {str(e)}")

    def search_products(
        self, ctx: Context, query: str, limit: int = 50
    ) -> Dict[str, Any]:
        """Search products by name or code.

        Args:
            ctx: MCP context
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            Search results

        Raises:
            ToolError: If search fails
        """
        try:
            if not query or not query.strip():
                raise ToolError("Search query is required")

            search_term = query.strip().lower()
            logger.info(f"Searching products: '{search_term}'")

            # Get all products and filter
            all_products = self.product_manager.list_all_products()

            filtered_products = []
            for product in all_products:
                if (
                    search_term in product["code"].lower()
                    or search_term in product["name"].lower()
                ):
                    filtered_products.append(
                        {
                            "code": product["code"],
                            "name": product["name"],
                            "created_at": product.get("created_at"),
                        }
                    )

            # Limit results
            results = filtered_products[:limit]

            response = {
                "success": True,
                "query": search_term,
                "results": results,
                "total_found": len(filtered_products),
                "returned": len(results),
            }

            logger.info(
                f"Search returned {len(results)} results for query: '{search_term}'"
            )
            return response

        except ToolError:
            raise

        except Exception as e:
            logger.error(f"Product search failed: {e}")
            raise ToolError(f"Failed to search products: {str(e)}")
