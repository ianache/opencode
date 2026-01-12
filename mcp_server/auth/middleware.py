"""
Authentication middleware for MCP server.

Provides JWT token validation and user authentication
for MCP server requests.
"""

import os
from typing import Any, Callable, Dict, Optional

from fastmcp import Context, ToolError
from loguru import logger

from mcp.auth.jwt_handler import JWTHandler


class AuthMiddleware:
    """Authentication middleware for MCP server."""

    def __init__(self, jwt_handler: Optional[JWTHandler] = None):
        """Initialize authentication middleware.

        Args:
            jwt_handler: JWT handler instance, creates one if not provided
        """
        self.jwt_handler = jwt_handler or JWTHandler()
        self.auth_enabled = os.getenv("MCP_AUTH_ENABLED", "true").lower() == "true"

    def require_auth(self, func: Callable) -> Callable:
        """Decorator to require authentication for MCP tools.

        Args:
            func: MCP tool function to protect

        Returns:
            Decorated function with authentication check
        """

        def wrapper(ctx: Context, *args, **kwargs):
            if not self.auth_enabled:
                # Skip authentication if disabled
                return func(ctx, *args, **kwargs)

            try:
                # Extract token from context metadata
                auth_token = self._extract_token_from_context(ctx)

                if not auth_token:
                    raise ToolError("Authentication required: No token provided")

                # Validate token
                payload = self.jwt_handler.validate_token(auth_token)

                # Add user info to context
                ctx.metadata = ctx.metadata or {}
                ctx.metadata["user"] = payload
                ctx.metadata["user_id"] = payload.get("sub")
                ctx.metadata["username"] = payload.get("username")

                logger.info(f"Authenticated request from user: {payload.get('sub')}")

                return func(ctx, *args, **kwargs)

            except Exception as e:
                logger.warning(f"Authentication failed: {str(e)}")
                raise ToolError(f"Authentication failed: {str(e)}")

        return wrapper

    def optional_auth(self, func: Callable) -> Callable:
        """Decorator to add optional authentication for MCP tools.

        Args:
            func: MCP tool function to optionally protect

        Returns:
            Decorated function with optional authentication
        """

        def wrapper(ctx: Context, *args, **kwargs):
            if not self.auth_enabled:
                return func(ctx, *args, **kwargs)

            try:
                # Extract token from context metadata
                auth_token = self._extract_token_from_context(ctx)

                if auth_token:
                    # Validate token and add user info to context
                    payload = self.jwt_handler.validate_token(auth_token)
                    ctx.metadata = ctx.metadata or {}
                    ctx.metadata["user"] = payload
                    ctx.metadata["user_id"] = payload.get("sub")
                    ctx.metadata["username"] = payload.get("username")

                    logger.info(
                        f"Authenticated request from user: {payload.get('sub')}"
                    )
                else:
                    logger.debug("Request without authentication token")

                return func(ctx, *args, **kwargs)

            except Exception as e:
                logger.warning(f"Optional authentication failed: {str(e)}")
                # Continue without authentication for optional auth
                return func(ctx, *args, **kwargs)

        return wrapper

    def _extract_token_from_context(self, ctx: Context) -> Optional[str]:
        """Extract JWT token from context.

        Args:
            ctx: MCP context object

        Returns:
            JWT token string if found, None otherwise
        """
        # Try to get token from various possible locations
        metadata = ctx.metadata or {}

        # Check for direct token
        if "auth_token" in metadata:
            return metadata["auth_token"]

        # Check for Authorization header
        if "authorization" in metadata:
            try:
                return self.jwt_handler.extract_token_from_header(
                    metadata["authorization"]
                )
            except ValueError:
                pass

        # Check for token in request headers
        headers = metadata.get("headers", {})
        if "authorization" in headers:
            try:
                return self.jwt_handler.extract_token_from_header(
                    headers["authorization"]
                )
            except ValueError:
                pass

        return None

    def generate_auth_response(self, username: str, password: str) -> Dict[str, Any]:
        """Generate authentication response for valid credentials.

        Args:
            username: User's username
            password: User's password

        Returns:
            Dictionary containing token and user info

        Raises:
            ToolError: If credentials are invalid
        """
        # Simple authentication - in production, use proper user database
        if self._validate_credentials(username, password):
            token = self.jwt_handler.generate_user_token(username)

            return {
                "success": True,
                "token": token,
                "user_id": username,
                "username": username,
                "expires_in": 86400,  # 24 hours in seconds
            }
        else:
            raise ToolError("Invalid credentials: Username or password incorrect")

    def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate user credentials.

        Args:
            username: User's username
            password: User's password

        Returns:
            True if credentials are valid, False otherwise
        """
        # Simple validation for demonstration
        # In production, use proper authentication mechanism
        valid_users = {"admin": "admin123", "user": "user123"}

        return valid_users.get(username) == password

    def get_current_user(self, ctx: Context) -> Optional[Dict[str, Any]]:
        """Get current authenticated user from context.

        Args:
            ctx: MCP context object

        Returns:
            User information if authenticated, None otherwise
        """
        metadata = ctx.metadata or {}
        return metadata.get("user")

    def is_authenticated(self, ctx: Context) -> bool:
        """Check if current request is authenticated.

        Args:
            ctx: MCP context object

        Returns:
            True if authenticated, False otherwise
        """
        return self.get_current_user(ctx) is not None

    def require_role(self, required_role: str) -> Callable:
        """Decorator to require specific user role.

        Args:
            required_role: Required user role

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            def wrapper(ctx: Context, *args, **kwargs):
                if not self.auth_enabled:
                    return func(ctx, *args, **kwargs)

                user = self.get_current_user(ctx)
                if not user:
                    raise ToolError("Authentication required")

                user_role = user.get("role", "user")
                if user_role != required_role:
                    raise ToolError(
                        f"Insufficient privileges: Role '{required_role}' required"
                    )

                return func(ctx, *args, **kwargs)

            return wrapper

        return decorator
