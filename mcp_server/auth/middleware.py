"""
Authentication middleware for MCP server.

Provides JWT token validation and user authentication
for MCP server requests.
"""

import bcrypt
import os
from typing import Any, Callable, Dict, Optional

from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger

from mcp_server.auth.jwt_handler import JWTHandler


class SecureUserStore:
    """Secure user store with bcrypt password hashing."""

    def __init__(self):
        """Initialize secure user store with hashed passwords."""
        self.users = self._initialize_secure_users()

    def _initialize_secure_users(self) -> Dict[str, Dict[str, str]]:
        """Initialize users with secure password hashing."""
        users = {
            "admin": {
                "password_hash": self._hash_password("admin123"),
                "role": "admin",
            },
            "user": {"password_hash": self._hash_password("user123"), "role": "user"},
        }
        logger.info(f"Initialized secure user store with {len(users)} users")
        return users

    def _hash_password(self, password: str) -> str:
        """Hash password with bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def _validate_password(self, password: str, hash_value: str) -> bool:
        """Validate password against stored hash."""
        try:
            return bcrypt.checkpw(password.encode(), hash_value.encode())
        except Exception as e:
            logger.error(f"Password validation error: {e}")
            return False

    def get_user(self, username: str) -> Optional[Dict[str, str]]:
        """Get user information securely."""
        return self.users.get(username)

    def validate_credentials(self, username: str, password: str) -> bool:
        """Validate user credentials securely."""
        user = self.get_user(username)
        if not user:
            logger.warning(f"User '{username}' not found")
            return False

        return self._validate_password(password, user["password_hash"])


class AuthMiddleware:
    """Authentication middleware for MCP server."""

    def __init__(self, jwt_handler: Optional[JWTHandler] = None):
        """Initialize authentication middleware.

        Args:
            jwt_handler: JWT handler instance, creates one if not provided
        """
        self.jwt_handler = jwt_handler or JWTHandler()
        self.auth_enabled = os.getenv("MCP_AUTH_ENABLED", "true").lower() == "true"
        self.user_store = SecureUserStore()

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
                # Extract token from context
                auth_token = self._extract_token_from_context(ctx)

                if not auth_token:
                    raise ToolError("Authentication required: No token provided")

                # Validate token
                payload = self.jwt_handler.validate_token(auth_token)

                logger.info(f"Authenticated request from user: {payload.get('sub')}")

                # For now, we'll continue without storing user info in context
                # since fastmcp Context doesn't support custom attributes
                # TODO: Implement proper user context management

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
                # Extract token from context
                auth_token = self._extract_token_from_context(ctx)

                if auth_token:
                    # Validate token
                    payload = self.jwt_handler.validate_token(auth_token)

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
        """Extract JWT token from FastMCP context using get_http_headers.

        Args:
            ctx: MCP context object

        Returns:
            JWT token string if found, None otherwise
        """
        try:
            # Import FastMCP's get_http_headers function
            from fastmcp.server.dependencies import get_http_headers

            # Get headers from FastMCP context
            headers = get_http_headers()

            # Debug logging
            logger.debug(f"FastMCP headers: {headers}")

            if headers and isinstance(headers, dict):
                auth_header = headers.get("authorization")
                if auth_header:
                    logger.info(f"Raw auth header: {auth_header}")
                    try:
                        token = self.jwt_handler.extract_token_from_header(auth_header)
                        logger.info(f"Token extracted from FastMCP headers: {token}")
                        return token
                    except ValueError as e:
                        logger.debug(f"Failed to extract token: {e}")
                        # Return raw token for testing purposes
                        return auth_header

        except ImportError:
            logger.debug("FastMCP get_http_headers not available")
        except Exception as e:
            logger.debug(f"Error extracting token from FastMCP context: {e}")

        # Fallback to other methods
        try:
            # Debug: Log all available attributes in context
            print(f"[DEBUG] Context attributes: {dir(ctx)}")
            logger.info(f"Context attributes: {dir(ctx)}")

            # Check if context has metadata or other container for headers
            if hasattr(ctx, "metadata") and ctx.metadata:  # type: ignore
                logger.debug(f"Context metadata: {ctx.metadata}")  # type: ignore
                if isinstance(ctx.metadata, dict):  # type: ignore
                    headers = ctx.metadata.get("headers") or ctx.metadata  # type: ignore
                    if isinstance(headers, dict) and "authorization" in headers:
                        try:
                            token = self.jwt_handler.extract_token_from_header(
                                headers["authorization"]
                            )
                            logger.info(
                                "Token extracted from metadata.headers.authorization"
                            )
                            return token
                        except ValueError as e:
                            logger.debug(
                                f"Failed to extract token from metadata headers: {e}"
                            )

            # Try accessing private attributes (if they exist)
            if hasattr(ctx, "_headers"):  # type: ignore
                headers = ctx._headers  # type: ignore
                logger.debug(f"Context _headers: {headers}")
                if isinstance(headers, dict) and "authorization" in headers:
                    try:
                        token = self.jwt_handler.extract_token_from_header(
                            headers["authorization"]
                        )
                        logger.info("Token extracted from _headers.authorization")
                        return token
                    except ValueError as e:
                        logger.debug(f"Failed to extract token from _headers: {e}")

        except Exception as e:
            logger.debug(f"Error in fallback token extraction: {e}")

        logger.warning("No authentication token found in context")
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
        """Validate user credentials securely.

        Args:
            username: User's username
            password: User's password

        Returns:
            True if credentials are valid, False otherwise
        """
        return self.user_store.validate_credentials(username, password)

    def get_current_user(self, ctx: Context) -> Optional[Dict[str, Any]]:
        """Get current authenticated user from context.

        Args:
            ctx: MCP context object

        Returns:
            User information if authenticated, None otherwise
        """
        # Since fastmcp Context doesn't support metadata,
        # we'll return None for now
        # TODO: Implement proper user context management
        try:
            if hasattr(ctx, "user_info"):  # type: ignore
                return ctx.user_info  # type: ignore
        except Exception:
            pass
        return None

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
