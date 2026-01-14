"""
MCP configuration settings.

Provides configuration management for MCP server
including authentication, transport, and Neo4j settings.
"""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class MCPServerConfig(BaseSettings):
    """Configuration settings for MCP server."""

    # Server Configuration
    server_name: str = Field(
        default="Product Management MCP Server", description="MCP server name"
    )
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    transport: str = Field(
        default="sse", description="Transport protocol (sse, stdio, websocket)"
    )

    # Authentication Configuration
    auth_enabled: bool = Field(default=True, description="Enable authentication")
    jwt_secret_key: str = Field(
        default="", description="JWT secret key for authentication"
    )
    jwt_secret_key_file: str = Field(
        default="", description="Path to JWT secret key file (for Docker secrets)"
    )
    jwt_expiry_hours: int = Field(default=24, description="JWT token expiry in hours")

    # Neo4j Configuration
    neo4j_uri: str = Field(default="", description="Neo4j connection URI")
    neo4j_username: str = Field(default="", description="Neo4j username")
    neo4j_password: str = Field(default="", description="Neo4j password")
    neo4j_database: str = Field(default="neo4j", description="Neo4j database name")

    # Security Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="CORS allowed origins",
    )
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_requests: bool = Field(default=True, description="Log incoming requests")

    # Development Configuration
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    reload_on_change: bool = Field(
        default=False, description="Auto-reload on code changes"
    )

    class Config:
        env_prefix = "MCP_"
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        """Initialize configuration with environment variable fallback."""
        super().__init__(**kwargs)

        # Load Neo4j settings from main config if not set
        if not self.neo4j_uri:
            # Try to get from existing settings
            try:
                from config.settings import get_settings

                main_settings = get_settings()
                self.neo4j_uri = main_settings.neo4j_uri
                self.neo4j_username = main_settings.neo4j_username
                self.neo4j_password = main_settings.neo4j_password
                self.neo4j_database = main_settings.neo4j_database
            except ImportError:
                pass

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate configuration settings."""
        if self.auth_enabled:
            jwt_secret = self.jwt_secret_key or self._get_jwt_secret_from_file()
            if not jwt_secret:
                raise ValueError(
                    "JWT_SECRET_KEY or JWT_SECRET_KEY_FILE must be set when authentication is enabled"
                )

        if self.transport not in ["sse", "stdio", "websocket"]:
            raise ValueError(
                f"Invalid transport: {self.transport}. Must be 'sse', 'stdio', or 'websocket'"
            )

        if not (1 <= self.port <= 65535):
            raise ValueError("Port must be between 1 and 65535")

    def _get_jwt_secret_from_file(self) -> Optional[str]:
        """Get JWT secret from file if configured."""
        secret_file = self.jwt_secret_key_file
        if secret_file and os.path.exists(secret_file):
            try:
                with open(secret_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                return None
        return None

    def get_cors_config(self) -> dict:
        """Get CORS configuration for FastAPI."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["*"],
        }

    def get_jwt_config(self) -> dict:
        """Get JWT configuration."""
        return {
            "secret_key": self.jwt_secret_key,
            "algorithm": "HS256",
            "token_expiry_hours": self.jwt_expiry_hours,
        }

    def get_neo4j_config(self) -> dict:
        """Get Neo4j connection configuration."""
        return {
            "uri": self.neo4j_uri,
            "username": self.neo4j_username,
            "password": self.neo4j_password,
            "database": self.neo4j_database,
        }

    @property
    def server_url(self) -> str:
        """Get full server URL."""
        if self.transport == "sse":
            return f"http://{self.host}:{self.port}"
        elif self.transport == "websocket":
            return f"ws://{self.host}:{self.port}"
        else:
            return f"stdio://{self.host}:{self.port}"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug_mode or os.getenv("ENVIRONMENT") == "development"

    @property
    def log_config(self) -> dict:
        """Get logging configuration."""
        return {
            "level": self.log_level,
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            "rotation": "10 MB",
            "retention": "7 days",
        }


class MCPDatabaseConfig(BaseSettings):
    """Database-specific configuration for MCP."""

    # Connection Pool Configuration
    max_connections: int = Field(default=10, description="Maximum database connections")
    connection_timeout: int = Field(
        default=30, description="Connection timeout in seconds"
    )

    # Query Configuration
    query_timeout: int = Field(default=60, description="Query timeout in seconds")
    max_query_results: int = Field(default=1000, description="Maximum query results")

    # Cache Configuration
    enable_query_cache: bool = Field(default=True, description="Enable query caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")

    class Config:
        env_prefix = "MCP_DB_"
        env_file = ".env"
        case_sensitive = False
