"""
Main FastMCP server for Product Management API.

Creates and configures MCP server with authentication,
tools, and resources for product management.
"""

import os
from typing import Any, Dict, Optional

import uvicorn
from fastmcp import FastMCP, Context, ToolError
from loguru import logger

from mcp.auth.jwt_handler import JWTHandler
from mcp.auth.middleware import AuthMiddleware
from mcp.config.mcp_config import MCPServerConfig
from mcp.tools.product_tools import ProductTools
from mcp.tools.functionality_tools import FunctionalityTools
from mcp.resources.product_resources import ProductResources


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
    mcp = FastMCP(
        name=config.server_name,
        transport=config.transport,
        host=config.host,
        port=config.port,
    )

    # Initialize authentication
    jwt_handler = JWTHandler(config.jwt_secret_key)
    auth_middleware = AuthMiddleware(jwt_handler)

    # Initialize tools and resources
    product_tools = ProductTools(auth_middleware)
    functionality_tools = FunctionalityTools(auth_middleware)
    product_resources = ProductResources(auth_middleware)

    # Register authentication middleware
    mcp.add_middleware(auth_middleware.require_auth)

    # Register tools
    logger.info("Registering MCP tools...")

    # Product Management Tools
    mcp.add_tool(
        product_tools.register_product,
        name="register_product",
        description="Register a new product with optional functionalities. Validates required fields and creates relationships with functionalities according to the ontology model.",
    )

    mcp.add_tool(
        product_tools.get_product_details,
        name="get_product_details",
        description="Get detailed information about a specific product including functionalities, incidents, and resolutions.",
    )

    mcp.add_tool(
        product_tools.update_product,
        name="update_product",
        description="Update product information. Only provided fields are updated.",
    )

    mcp.add_tool(
        product_tools.delete_product,
        name="delete_product",
        description="Delete a product and all its relationships including functionalities and incidents.",
    )

    mcp.add_tool(
        product_tools.list_products,
        name="list_products",
        description="List all products with pagination support.",
    )

    mcp.add_tool(
        product_tools.search_products,
        name="search_products",
        description="Search products by code or name with fuzzy matching.",
    )

    # Functionality Management Tools
    mcp.add_tool(
        functionality_tools.register_functionality,
        name="register_functionality",
        description="Register a new functionality for assignment to products.",
    )

    mcp.add_tool(
        functionality_tools.get_functionality_details,
        name="get_functionality_details",
        description="Get detailed information about a specific functionality including products, components, incidents, and resolutions.",
    )

    mcp.add_tool(
        functionality_tools.assign_functionalities_to_product,
        name="assign_functionalities_to_product",
        description="Assign multiple functionalities to a product in batch. Validates existence before assignment.",
    )

    mcp.add_tool(
        functionality_tools.remove_functionalities_from_product,
        name="remove_functionalities_from_product",
        description="Remove multiple functionalities from a product in batch.",
    )

    mcp.add_tool(
        functionality_tools.list_functionalities,
        name="list_functionalities",
        description="List all available functionalities with pagination support.",
    )

    # Authentication Tools
    mcp.add_tool(
        authenticate_user,
        name="authenticate_user",
        description="Authenticate user credentials and return JWT token for API access.",
        auth_required=False,  # No authentication required for login
    )

    # Register resources
    logger.info("Registering MCP resources...")

    mcp.add_resource(
        product_resources.products_resource,
        uri="products://",
        description="List all products with pagination. Supports query parameters: limit, offset",
    )

    mcp.add_resource(
        product_resources.product_resource,
        uri="product://{product_code}",
        description="Access detailed information for a specific product",
    )

    mcp.add_resource(
        product_resources.functionalities_resource,
        uri="functionalities://",
        description="List all available functionalities with pagination. Supports query parameters: limit, offset",
    )

    mcp.add_resource(
        product_resources.search_resource,
        uri="search://",
        description="Search products and functionalities. Supports query parameters: query, type, limit",
    )

    mcp.add_resource(
        product_resources.schema_resource,
        uri="schema://",
        description="Access schema information for products, functionalities, or complete ontology. Supports query parameter: type",
    )

    # Server info resource
    mcp.add_resource(
        server_info_resource,
        uri="server://info",
        description="Get server information and status",
    )

    logger.info(
        f"MCP server initialized with {len(mcp.tools)} tools and {len(mcp.resources)} resources"
    )
    return mcp


def authenticate_user(ctx: Context, username: str, password: str) -> Dict[str, Any]:
    """Authenticate user and generate JWT token.

    Args:
        ctx: MCP context
        username: User's username
        password: User's password

    Returns:
        Authentication result with JWT token

    Raises:
        ToolError: If authentication fails
    """
    try:
        # This bypasses auth middleware since login doesn't require authentication
        jwt_handler = JWTHandler()
        auth_result = jwt_handler.generate_auth_response(username, password)

        logger.info(f"User authenticated: {username}")

        return {
            "success": True,
            "message": "Authentication successful",
            "username": username,
            "token": auth_result["token"],
            "expires_in": auth_result["expires_in"],
        }

    except ToolError:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise ToolError(f"Authentication failed: {str(e)}")


def server_info_resource(ctx: Context) -> Dict[str, Any]:
    """Resource for server information.

    Args:
        ctx: MCP context

    Returns:
        Server information and status
    """
    try:
        from mcp.config.mcp_config import MCPServerConfig

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
                "endpoints": {
                    "tools": len(create_mcp_server().tools),
                    "resources": len(create_mcp_server().resources),
                },
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
    logger.configure(**config.log_config)

    try:
        if config.transport == "sse":
            # Run with SSE transport using uvicorn
            uvicorn.run(
                mcp.app,
                host=config.host,
                port=config.port,
                log_level=config.log_level.lower(),
                access_log=config.log_requests,
                reload=config.reload_on_change,
            )
        else:
            # Run with stdio or websocket transport
            mcp.run()

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
