"""
Authentication initialization for MCP package.
"""

from .jwt_handler import JWTHandler
from .middleware import AuthMiddleware

__all__ = ["JWTHandler", "AuthMiddleware"]
