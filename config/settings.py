"""
Settings and configuration management for GraphRAG application.

Handles environment variable loading, validation,
and provides centralized configuration access.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""

    pass


class Settings:
    """Application settings with environment variable support."""

    def __init__(self) -> None:
        # Load environment variables from .env file
        load_dotenv()

        # Neo4j Configuration
        self.neo4j_uri: str = os.getenv("NEO4J_URI", "")
        self.neo4j_username: str = os.getenv("NEO4J_USERNAME", "")
        self.neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")
        self.neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")

        # Application Configuration
        self.app_name: str = "GraphRAG"
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

        # Data Configuration
        self.news_data_url: str = os.getenv(
            "NEWS_DATA_URL",
            "https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/news_articles.csv",
        )

        # Validate required settings
        self._validate()

    def _validate(self) -> None:
        """Validate that required configuration is present."""
        required_vars = {
            "NEO4J_URI": self.neo4j_uri,
            "NEO4J_USERNAME": self.neo4j_username,
            "NEO4J_PASSWORD": self.neo4j_password,
        }

        missing_vars = [
            var_name for var_name, value in required_vars.items() if not value.strip()
        ]

        if missing_vars:
            error_msg = (
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            raise ConfigurationError(
                f"{error_msg}. Please set up your .env file based on .env.example"
            )

    def __str__(self) -> str:
        """Return string representation of settings (excluding sensitive data)."""
        return (
            f"Settings("
            f"app_name='{self.app_name}', "
            f"neo4j_uri='{self.neo4j_uri}', "
            f"neo4j_username='{self.neo4j_username}', "
            f"neo4j_database='{self.neo4j_database}', "
            f"log_level='{self.log_level}')"
        )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance, creating it if necessary."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
