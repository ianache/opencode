"""
MCP resources for product data access.

Provides MCP resource endpoints for accessing product information,
functionality data, and schema information.
"""

from typing import Any, Dict, List, Optional

from fastmcp import Context
from loguru import logger

from graph.neo4j_client import create_neo4j_client
from graph.product_manager import ProductManager


class ProductResources:
    """MCP resources for product data access."""

    def __init__(self, auth_middleware=None):
        """Initialize product resources with optional authentication.

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

    def products_resource(
        self, ctx: Context, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """Resource for listing all products.

        Resource URI: products://?limit=50&offset=0

        Args:
            ctx: MCP context
            limit: Maximum products to return
            offset: Number of products to skip

        Returns:
            List of products with pagination
        """
        try:
            logger.info(f"Accessing products resource: limit={limit}, offset={offset}")

            # Validate parameters
            if not (1 <= limit <= 1000):
                limit = 50
            if offset < 0:
                offset = 0

            # Get products
            all_products = self.product_manager.list_all_products()

            # Apply pagination
            total = len(all_products)
            paginated_products = all_products[offset : offset + limit]

            response = {
                "uri": "products://",
                "data": [
                    {
                        "code": product["code"],
                        "name": product["name"],
                        "created_at": product.get("created_at"),
                        "updated_at": product.get("updated_at"),
                    }
                    for product in paginated_products
                ],
                "metadata": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total,
                },
                "links": {
                    "self": f"products://?limit={limit}&offset={offset}",
                    "next": f"products://?limit={limit}&offset={offset + limit}"
                    if offset + limit < total
                    else None,
                    "first": "products://?limit=50&offset=0",
                },
            }

            logger.info(f"Products resource accessed: {len(response['data'])} items")
            return response

        except Exception as e:
            logger.error(f"Failed to access products resource: {e}")
            raise Exception(f"Products resource access failed: {str(e)}")

    def product_resource(self, ctx: Context, product_code: str) -> Dict[str, Any]:
        """Resource for accessing a specific product.

        Resource URI: product://{product_code}

        Args:
            ctx: MCP context
            product_code: Product unique identifier

        Returns:
            Detailed product information
        """
        try:
            logger.info(f"Accessing product resource: {product_code}")

            product_details = self.product_manager.get_product_with_functionalities(
                product_code
            )

            if not product_details or not product_details.get("p"):
                return {
                    "uri": f"product://{product_code}",
                    "error": f"Product '{product_code}' not found",
                    "data": None,
                }

            product = product_details["p"]
            functionalities = product_details.get("functionalities", [])
            incidents = product_details.get("incidents", [])
            resolutions = product_details.get("resolutions", [])

            response = {
                "uri": f"product://{product_code}",
                "data": {
                    "code": product["code"],
                    "name": product["name"],
                    "created_at": product.get("created_at"),
                    "updated_at": product.get("updated_at"),
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
                },
                "metadata": {
                    "last_modified": product.get("updated_at")
                    or product.get("created_at"),
                    "functionality_count": len(functionalities),
                    "incident_count": len(incidents),
                    "resolution_count": len(resolutions),
                },
                "links": {
                    "self": f"product://{product_code}",
                    "functionalities": f"product://{product_code}/functionalities",
                    "incidents": f"product://{product_code}/incidents",
                    "products": "products://",
                },
            }

            logger.info(f"Product resource accessed: {product_code}")
            return response

        except Exception as e:
            logger.error(f"Failed to access product resource: {e}")
            raise Exception(f"Product resource access failed: {str(e)}")

    def functionalities_resource(
        self, ctx: Context, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """Resource for listing all functionalities.

        Resource URI: functionalities://?limit=50&offset=0

        Args:
            ctx: MCP context
            limit: Maximum functionalities to return
            offset: Number of functionalities to skip

        Returns:
            List of functionalities with pagination
        """
        try:
            logger.info(
                f"Accessing functionalities resource: limit={limit}, offset={offset}"
            )

            # Validate parameters
            if not (1 <= limit <= 1000):
                limit = 50
            if offset < 0:
                offset = 0

            # Get all products and extract unique functionalities
            products_summary = self.product_manager.get_all_products_summary()

            # This is a simplified approach - collect from existing data
            all_functionalities = []

            # Get functionalitites by checking each product
            for summary in products_summary:
                product_code = summary.get("product_code")
                if product_code:
                    try:
                        product_details = (
                            self.product_manager.get_product_with_functionalities(
                                product_code
                            )
                        )
                        functionalities = product_details.get("functionalities", [])

                        for func in functionalities:
                            # Add to list if not already present
                            if not any(
                                f["code"] == func["code"] for f in all_functionalities
                            ):
                                all_functionalities.append(
                                    {
                                        "code": func["code"],
                                        "name": func["name"],
                                        "created_at": func.get("created_at"),
                                    }
                                )
                    except Exception:
                        continue

            # Apply pagination
            total = len(all_functionalities)
            paginated_functionalities = all_functionalities[offset : offset + limit]

            response = {
                "uri": "functionalities://",
                "data": paginated_functionalities,
                "metadata": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total,
                },
                "links": {
                    "self": f"functionalities://?limit={limit}&offset={offset}",
                    "next": f"functionalities://?limit={limit}&offset={offset + limit}"
                    if offset + limit < total
                    else None,
                    "first": "functionalities://?limit=50&offset=0",
                },
            }

            logger.info(
                f"Functionalities resource accessed: {len(response['data'])} items"
            )
            return response

        except Exception as e:
            logger.error(f"Failed to access functionalities resource: {e}")
            raise Exception(f"Functionalities resource access failed: {str(e)}")

    def search_resource(
        self, ctx: Context, query: str, type: str = "products", limit: int = 20
    ) -> Dict[str, Any]:
        """Resource for searching products or functionalities.

        Resource URI: search://?query=term&type=products&limit=20

        Args:
            ctx: MCP context
            query: Search term
            type: Search type (products, functionalities, all)
            limit: Maximum results to return

        Returns:
            Search results
        """
        try:
            if not query or not query.strip():
                return {
                    "uri": f"search://?query=&type={type}",
                    "error": "Search query is required",
                    "data": None,
                }

            search_term = query.strip().lower()
            search_type = type.lower()
            logger.info(
                f"Search resource: query='{search_term}', type={search_type}, limit={limit}"
            )

            results = []

            if search_type in ["products", "all"]:
                # Search products
                all_products = self.product_manager.list_all_products()
                for product in all_products:
                    if (
                        search_term in product["code"].lower()
                        or search_term in product["name"].lower()
                    ):
                        results.append(
                            {
                                "type": "product",
                                "code": product["code"],
                                "name": product["name"],
                                "created_at": product.get("created_at"),
                                "relevance": self._calculate_relevance(
                                    search_term, product["code"], product["name"]
                                ),
                            }
                        )

            if search_type in ["functionalities", "all"]:
                # Search functionalities (simplified approach)
                products_summary = self.product_manager.get_all_products_summary()
                for summary in products_summary:
                    product_code = summary.get("product_code")
                    if product_code:
                        try:
                            product_details = (
                                self.product_manager.get_product_with_functionalities(
                                    product_code
                                )
                            )
                            functionalities = product_details.get("functionalities", [])

                            for func in functionalities:
                                if (
                                    search_term in func["code"].lower()
                                    or search_term in func["name"].lower()
                                ):
                                    results.append(
                                        {
                                            "type": "functionality",
                                            "code": func["code"],
                                            "name": func["name"],
                                            "created_at": func.get("created_at"),
                                            "product_code": product_code,
                                            "relevance": self._calculate_relevance(
                                                search_term, func["code"], func["name"]
                                            ),
                                        }
                                    )
                        except Exception:
                            continue

            # Sort by relevance and limit results
            results.sort(key=lambda x: x["relevance"], reverse=True)
            limited_results = results[:limit]

            response = {
                "uri": f"search://?query={search_term}&type={search_type}&limit={limit}",
                "data": limited_results,
                "metadata": {
                    "query": search_term,
                    "type": search_type,
                    "total_found": len(results),
                    "returned": len(limited_results),
                    "limit": limit,
                },
                "links": {
                    "self": f"search://?query={search_term}&type={search_type}&limit={limit}",
                    "products": "products://",
                    "functionalities": "functionalities://",
                },
            }

            logger.info(
                f"Search resource completed: {len(limited_results)} results for '{search_term}'"
            )
            return response

        except Exception as e:
            logger.error(f"Search resource failed: {e}")
            raise Exception(f"Search resource failed: {str(e)}")

    def schema_resource(self, ctx: Context, type: str = "product") -> Dict[str, Any]:
        """Resource for accessing schema information.

        Resource URI: schema://?type=product

        Args:
            ctx: MCP context
            type: Schema type (product, functionality, ontology)

        Returns:
            Schema information
        """
        try:
            logger.info(f"Accessing schema resource: type={type}")

            if type == "product":
                schema = {
                    "type": "product",
                    "description": "Product node schema",
                    "properties": {
                        "code": {
                            "type": "string",
                            "required": True,
                            "description": "Product unique identifier",
                            "max_length": 20,
                        },
                        "name": {
                            "type": "string",
                            "required": True,
                            "description": "Product descriptive name",
                            "max_length": 200,
                        },
                        "created_at": {
                            "type": "datetime",
                            "required": False,
                            "description": "Creation timestamp",
                        },
                        "updated_at": {
                            "type": "datetime",
                            "required": False,
                            "description": "Last update timestamp",
                        },
                    },
                    "relationships": {
                        "ASIGNACION_FUNCIONALIDAD": {
                            "type": "functionality",
                            "direction": "outgoing",
                            "description": "Product has assigned functionalities",
                        }
                    },
                }
            elif type == "functionality":
                schema = {
                    "type": "functionality",
                    "description": "Functionality node schema",
                    "properties": {
                        "code": {
                            "type": "string",
                            "required": True,
                            "description": "Functionality unique identifier",
                            "max_length": 20,
                        },
                        "name": {
                            "type": "string",
                            "required": True,
                            "description": "Functionality descriptive name",
                            "max_length": 200,
                        },
                        "created_at": {
                            "type": "datetime",
                            "required": False,
                            "description": "Creation timestamp",
                        },
                    },
                    "relationships": {
                        "HAS_INCIDENT": {
                            "type": "incident",
                            "direction": "outgoing",
                            "description": "Functionality has incidents",
                        }
                    },
                }
            elif type == "ontology":
                schema = {
                    "type": "ontology",
                    "description": "Complete product management ontology",
                    "node_types": {
                        "Product": {
                            "description": "Software product or system",
                            "properties": ["code", "name", "created_at", "updated_at"],
                        },
                        "Functionality": {
                            "description": "Product functionality or feature",
                            "properties": ["code", "name", "created_at"],
                        },
                        "Component": {
                            "description": "Architectural component",
                            "properties": ["code", "name", "created_at"],
                        },
                        "Incident": {
                            "description": "Reported incident",
                            "properties": [
                                "code",
                                "description",
                                "sla_level",
                                "created_at",
                            ],
                        },
                        "Resolution": {
                            "description": "Incident resolution",
                            "properties": [
                                "incident_code",
                                "procedure",
                                "resolution_date",
                                "created_at",
                            ],
                        },
                    },
                    "relationship_types": {
                        "ASIGNACION_FUNCIONALIDAD": {
                            "description": "Assignment of functionality to product or component",
                            "from": ["Product", "Component"],
                            "to": "Functionality",
                        },
                        "HAS_INCIDENT": {
                            "description": "Functionality has incident",
                            "from": "Functionality",
                            "to": "Incident",
                        },
                        "HAS_RESOLUTION": {
                            "description": "Incident has resolution",
                            "from": "Incident",
                            "to": "Resolution",
                        },
                    },
                }
            else:
                schema = {
                    "error": f"Unknown schema type: {type}",
                    "available_types": ["product", "functionality", "ontology"],
                }

            response = {
                "uri": f"schema://?type={type}",
                "data": schema,
                "metadata": {
                    "type": type,
                    "version": "1.0.0",
                    "last_updated": "2024-01-01",
                },
                "links": {
                    "self": f"schema://?type={type}",
                    "product": "schema://?type=product",
                    "functionality": "schema://?type=functionality",
                    "ontology": "schema://?type=ontology",
                },
            }

            logger.info(f"Schema resource accessed: {type}")
            return response

        except Exception as e:
            logger.error(f"Schema resource failed: {e}")
            raise Exception(f"Schema resource access failed: {str(e)}")

    def _calculate_relevance(self, query: str, code: str, name: str) -> float:
        """Calculate search relevance score.

        Args:
            query: Search query
            code: Item code
            name: Item name

        Returns:
            Relevance score (0.0 to 1.0)
        """
        query_lower = query.lower()
        code_lower = code.lower()
        name_lower = name.lower()

        score = 0.0

        # Exact match in code gets highest score
        if query_lower == code_lower:
            score += 1.0

        # Partial match in code
        if query_lower in code_lower:
            score += 0.8

        # Exact match in name
        if query_lower == name_lower:
            score += 0.7

        # Partial match in name
        if query_lower in name_lower:
            score += 0.5

        return min(score, 1.0)
