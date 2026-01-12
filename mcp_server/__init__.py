"""
MCP (Model Context Protocol) package for Product Management API.

This package provides MCP tools and resources for managing products
and functionalities through the Model Context Protocol using FastMCP.
"""

from .server import create_mcp_server

__version__ = "0.1.0"
__all__ = ["create_mcp_server"]
