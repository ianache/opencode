"""
JWT Handler for MCP authentication.

Provides JWT token generation, validation, and management
for MCP server authentication.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from loguru import logger


class JWTHandler:
    """Handles JWT token operations for MCP authentication."""

    def __init__(self, secret_key: Optional[str] = None):
        """Initialize JWT handler with secret key."""
        self.secret_key = secret_key or os.getenv(
            "JWT_SECRET_KEY", "default-secret-change-in-production"
        )
        self.algorithm = "HS256"
        self.token_expiry = timedelta(hours=24)

        if self.secret_key == "default-secret-change-in-production":
            logger.warning(
                "Using default JWT secret key - please set JWT_SECRET_KEY environment variable"
            )

    def generate_token(
        self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a JWT token for user authentication.

        Args:
            user_id: Unique user identifier
            additional_claims: Additional claims to include in token

        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + self.token_expiry,
            "iss": "graphrag-mcp-server",
            "aud": "graphrag-consumers",
        }

        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Generated JWT token for user: {user_id}")
        return token

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience="graphrag-consumers",
                issuer="graphrag-mcp-server",
            )
            logger.debug(f"Token validated successfully for user: {payload.get('sub')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token validation failed: Expired signature")
            raise jwt.InvalidTokenError("Token has expired")

        except jwt.InvalidAudienceError:
            logger.warning("Token validation failed: Invalid audience")
            raise jwt.InvalidTokenError("Invalid token audience")

        except jwt.InvalidIssuerError:
            logger.warning("Token validation failed: Invalid issuer")
            raise jwt.InvalidTokenError("Invalid token issuer")

        except jwt.InvalidTokenError as e:
            logger.warning(f"Token validation failed: {str(e)}")
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

    def refresh_token(self, token: str) -> str:
        """Refresh an existing token.

        Args:
            token: Current valid JWT token

        Returns:
            New JWT token
        """
        payload = self.validate_token(token)
        user_id = payload.get("sub")

        # Remove time-sensitive claims
        refresh_payload = {
            k: v for k, v in payload.items() if k not in ["iat", "exp", "nbf"]
        }

        return self.generate_token(user_id, refresh_payload)

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired without raising exception.

        Args:
            token: JWT token string

        Returns:
            True if token is expired, False otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},
            )
            exp = payload.get("exp")
            if exp:
                return datetime.utcnow().timestamp() > exp
            return False
        except jwt.InvalidTokenError:
            return True

    @staticmethod
    def extract_token_from_header(auth_header: str) -> str:
        """Extract JWT token from Authorization header.

        Args:
            auth_header: Authorization header value

        Returns:
            JWT token string

        Raises:
            ValueError: If header format is invalid
        """
        if not auth_header:
            raise ValueError("Authorization header is missing")

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise ValueError(
                "Invalid Authorization header format. Expected: 'Bearer <token>'"
            )

        return parts[1]

    def generate_user_token(self, username: str, user_id: Optional[str] = None) -> str:
        """Generate token for authenticated user.

        Args:
            username: User's username
            user_id: Optional custom user ID, defaults to username

        Returns:
            JWT token
        """
        user_id = user_id or username
        claims = {"username": username, "type": "user"}

        return self.generate_token(user_id, claims)
