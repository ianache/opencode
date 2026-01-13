"""
Main FastMCP server for Product Management API.

Creates and configures MCP server with authentication,
tools, and resources for product management.
"""

import os
from typing import Any, Dict, List, Optional, Literal

from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from loguru import logger

from mcp_server.auth.jwt_handler import JWTHandler
from mcp_server.auth.middleware import AuthMiddleware
from mcp_server.config.mcp_config import MCPServerConfig
from mcp_server.tools.product_tools import ProductTools
from mcp_server.tools.functionality_tools import FunctionalityTools
from mcp_server.tools.incident_tools import IncidentTools
from mcp_server.resources.product_resources import ProductResources


def create_mcp_server(config: Optional[MCPServerConfig] = None) -> FastMCP:
    """Create and configure the MCP server.

    Args:
        config: MCP server configuration, creates default if None

    Returns:
        Configured FastMCP server instance
    """
    # Initialize configuration
    if config is None:
        config = MCPServerConfig()

    logger.info(f"Initializing MCP server: {config.server_name}")

    # Create FastMCP server
    mcp = FastMCP(name=config.server_name)

    # Initialize authentication
    jwt_handler = JWTHandler(config.jwt_secret_key)
    auth_middleware = AuthMiddleware(jwt_handler)

    # Initialize tools and resources
    product_tools = ProductTools(auth_middleware)
    functionality_tools = FunctionalityTools(auth_middleware)
    incident_tools = IncidentTools(auth_middleware)
    product_resources = ProductResources(auth_middleware)

    # Register tools with decorators
    logger.info("Registering MCP tools...")

    # Product Management Tools
    @mcp.tool()
    def register_product(
        ctx: Context, code: str, name: str, functionalities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Register a new product with optional functionalities. Validates required fields and creates relationships with functionalities according to the ontology model."""
        return product_tools.register_product(ctx, code, name, functionalities or [])

    @mcp.tool()
    def get_product_details(ctx: Context, code: str) -> Dict[str, Any]:
        """Get detailed information about a specific product including functionalities, incidents, and resolutions."""
        return product_tools.get_product_details(ctx, code)

    @mcp.tool()
    def update_product(
        ctx: Context, code: str, name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update product information. Only provided fields are updated."""
        return product_tools.update_product(ctx, code, name)

    @mcp.tool()
    def delete_product(ctx: Context, code: str) -> Dict[str, Any]:
        """Delete a product and all its relationships including functionalities and incidents."""
        return product_tools.delete_product(ctx, code)

    @mcp.tool()
    def list_products(ctx: Context, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List all products with pagination support."""
        return product_tools.list_products(ctx, limit, offset)

    @mcp.tool()
    def search_products(ctx: Context, query: str, limit: int = 50) -> Dict[str, Any]:
        """Search products by code or name with fuzzy matching."""
        return product_tools.search_products(ctx, query, limit)

    # Functionality Management Tools
    @mcp.tool()
    def register_functionality(ctx: Context, code: str, name: str) -> Dict[str, Any]:
        """Register a new functionality for assignment to products."""
        return functionality_tools.register_functionality(ctx, code, name)

    @mcp.tool()
    def get_functionality_details(ctx: Context, code: str) -> Dict[str, Any]:
        """Get detailed information about a specific functionality including products, components, incidents, and resolutions."""
        return functionality_tools.get_functionality_details(ctx, code)

    @mcp.tool()
    def assign_functionalities_to_product(
        ctx: Context, product_code: str, functionality_codes: List[str]
    ) -> Dict[str, Any]:
        """Assign multiple functionalities to a product in batch. Validates existence before assignment."""
        return functionality_tools.assign_functionalities_to_product(
            ctx, product_code, functionality_codes
        )

    @mcp.tool()
    def remove_functionalities_from_product(
        ctx: Context, product_code: str, functionality_codes: List[str]
    ) -> Dict[str, Any]:
        """Remove multiple functionalities from a product in batch."""
        return functionality_tools.remove_functionalities_from_product(
            ctx, product_code, functionality_codes
        )

    @mcp.tool()
    def list_functionalities(
        ctx: Context, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """List all available functionalities with pagination support."""
        return functionality_tools.list_functionalities(ctx, limit, offset)

    # Incident Management Tools
    @mcp.tool()
    def register_incident(
        ctx: Context,
        code: str,
        description: str,
        sla_level: str,
        functionality_code: str,
    ) -> Dict[str, Any]:
        """Register a new incident for a functionality. All fields from ontological model must be provided. Returns Spanish error message 'Datos incompletos proporcionados' if data is incomplete."""
        from mcp_server.models.requests import IncidentRegistrationRequest

        incident_data = IncidentRegistrationRequest(
            code=code,
            description=description,
            sla_level=sla_level,
            functionality_code=functionality_code,
        )
        return incident_tools.register_incident(ctx, incident_data)

    @mcp.tool()
    def get_incident_details(ctx: Context, incident_code: str) -> Dict[str, Any]:
        """Get detailed information about a specific incident."""
        return incident_tools.get_incident_details(ctx, incident_code)

    @mcp.tool()
    def list_incidents_by_functionality(
        ctx: Context, functionality_code: str, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """List all incidents for a specific functionality with pagination support."""
        return incident_tools.list_incidents_by_functionality(
            ctx, functionality_code, limit, offset
        )

    @mcp.tool()
    def list_incidents_by_product(
        ctx: Context, product_code: str, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """List all incidents for a specific product with pagination support."""
        return incident_tools.list_incidents_by_product(
            ctx, product_code, limit, offset
        )

    # Authentication Tools
    @mcp.tool()
    def authenticate_user(ctx: Context, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user credentials and return JWT token for API access."""
        try:
            # This bypasses auth middleware since login doesn't require authentication
            jwt_handler = JWTHandler()
            auth_middleware = AuthMiddleware(jwt_handler)
            auth_result = auth_middleware.generate_auth_response(username, password)

            logger.info(f"User authenticated: {username}")

            return {
                "success": True,
                "message": "Authentication successful",
                "username": username,
                "token": auth_result["token"],
                "expires_in": auth_result["expires_in"],
            }

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise ToolError(f"Authentication failed: {str(e)}")

    # Register resources with decorators
    logger.info("Registering MCP resources...")

    @mcp.resource("products://{limit}_{offset}")
    def products_resource(ctx: Context, limit: str, offset: str) -> Dict[str, Any]:
        """List all products with pagination. Supports query parameters: limit, offset"""
        return product_resources.products_resource(ctx, int(limit), int(offset))

    @mcp.resource("product://{product_code}")
    def product_resource(ctx: Context, product_code: str) -> Dict[str, Any]:
        """Access detailed information for a specific product"""
        return product_resources.product_resource(ctx, product_code)

    @mcp.resource("functionalities://{limit}_{offset}")
    def functionalities_resource(
        ctx: Context, limit: str, offset: str
    ) -> Dict[str, Any]:
        """List all available functionalities with pagination. Supports query parameters: limit, offset"""
        return product_resources.functionalities_resource(ctx, int(limit), int(offset))

    @mcp.resource("search://{query}")
    def search_resource(ctx: Context, query: str) -> Dict[str, Any]:
        """Search products and functionalities. Supports query parameters: query, type, limit"""
        return product_resources.search_resource(ctx, query, "", 50)

    @mcp.resource("schema://{type}")
    def schema_resource(ctx: Context, type: str) -> Dict[str, Any]:
        """Access schema information for products, functionalities, or complete ontology. Supports query parameter: type"""
        return product_resources.schema_resource(ctx, type)

    # Server info resource
    @mcp.resource("server://info")
    def server_info(ctx: Context) -> Dict[str, Any]:
        """Get server information and status"""
        return server_info_resource(ctx)

    logger.info("MCP server initialized with tools and resources")
    return mcp


def server_info_resource(ctx: Context) -> Dict[str, Any]:
    """Resource for server information.

    Args:
        ctx: MCP context

    Returns:
        Server information and status
    """
    try:
        from mcp_server.config.mcp_config import MCPServerConfig

        config = MCPServerConfig()

        info = {
            "uri": "server://info",
            "data": {
                "name": config.server_name,
                "version": "0.1.0",
                "transport": config.transport,
                "auth_enabled": config.auth_enabled,
                "host": config.host,
                "port": config.port,
                "status": "running",
                "uptime": "0m",  # Would need to track actual uptime
            },
            "metadata": {
                "api_version": "MCP/1.0",
                "supported_transports": ["sse", "stdio", "websocket"],
                "authentication": "JWT Bearer Token",
            },
            "links": {
                "self": "server://info",
                "tools": "tools://",
                "resources": "resources://",
                "schema": "schema://?type=ontology",
            },
        }

        logger.info("Server info resource accessed")
        return info

    except Exception as e:
        logger.error(f"Server info resource failed: {e}")
        raise Exception(f"Server info resource failed: {str(e)}")


def run_mcp_server(config: Optional[MCPServerConfig] = None) -> None:
    """Run the MCP server.

    Args:
        config: MCP server configuration
    """
    if config is None:
        config = MCPServerConfig()

    logger.info(f"Starting MCP server on {config.host}:{config.port}")

    # Create MCP server
    mcp = create_mcp_server(config)

    # Configure logging
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=config.log_level,
        format="{time} | {level} | {message}",
    )

    try:
        # Run with transport
        if config.transport == "sse":
            mcp.run(transport="sse", host=config.host, port=config.port)
        elif config.transport == "http":
            mcp.run(transport="http", host=config.host, port=config.port)
        elif config.transport == "stdio":
            mcp.run()
        else:
            # Use typing.cast for type compatibility
            from typing import cast

            mcp.run(
                transport=cast(
                    Literal["sse", "http", "stdio", "streamable-http"], config.transport
                )
            )

    except Exception as e:
        logger.error(f"MCP server failed to start: {e}")
        raise


def main() -> None:
    """Main entry point for MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="Product Management MCP Server")
    parser.add_argument(
        "--host", default=None, help="Server host (default: from config)"
    )
    parser.add_argument(
        "--port", type=int, default=None, help="Server port (default: from config)"
    )
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio", "websocket"],
        default=None,
        help="Transport protocol (default: from config)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Override config with command line arguments
    config = MCPServerConfig()
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port
    if args.transport:
        config.transport = args.transport
    if args.debug:
        config.debug_mode = True
        config.log_level = "DEBUG"

    # Run server
    run_mcp_server(config)


if __name__ == "__main__":
    main()
