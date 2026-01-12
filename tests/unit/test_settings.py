"""
Unit tests for configuration module.

Tests settings management, environment variable loading,
and configuration validation.
"""

import os
import sys
from unittest.mock import patch

import pytest

from config.settings import Settings, get_settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self):
        """Test settings with default values."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.app_name == "GraphRAG"
            assert settings.log_level == "INFO"
            assert settings.neo4j_database == "neo4j"

    def test_environment_variables_loaded(self):
        """Test that environment variables are loaded correctly."""
        test_env = {
            "NEO4J_URI": "bolt://test:7687",
            "NEO4J_USERNAME": "test_user",
            "NEO4J_PASSWORD": "test_pass",
            "NEO4J_DATABASE": "test_db",
            "LOG_LEVEL": "DEBUG",
        }

        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()
            assert settings.neo4j_uri == "bolt://test:7687"
            assert settings.neo4j_username == "test_user"
            assert settings.neo4j_password == "test_pass"
            assert settings.neo4j_database == "test_db"
            assert settings.log_level == "DEBUG"

    def test_missing_required_variables_causes_exit(self):
        """Test that missing required variables causes sys.exit."""
        test_env = {
            "NEO4J_URI": "bolt://test:7687",
            "NEO4J_USERNAME": "test_user",
            # Missing NEO4J_PASSWORD
        }

        with patch.dict(os.environ, test_env, clear=True):
            with patch("config.settings.load_dotenv"):  # Prevent .env loading
                # Clear any cached settings
                if hasattr(get_settings, "_settings"):
                    delattr(get_settings, "_settings")

                with pytest.raises(SystemExit) as exc_info:
                    Settings()
                assert exc_info.value.code == 1

    def test_empty_required_variables_causes_exit(self):
        """Test that empty required variables causes sys.exit."""
        test_env = {
            "NEO4J_URI": "",
            "NEO4J_USERNAME": "test_user",
            "NEO4J_PASSWORD": "test_pass",
        }

        with patch.dict(os.environ, test_env, clear=True):
            with pytest.raises(SystemExit) as exc_info:
                Settings()
            assert exc_info.value.code == 1

    def test_str_representation(self):
        """Test string representation excludes sensitive data."""
        test_env = {
            "NEO4J_URI": "bolt://test:7687",
            "NEO4J_USERNAME": "test_user",
            "NEO4J_PASSWORD": "secret_password",
        }

        with patch.dict(os.environ, test_env, clear=True):
            settings = Settings()
            str_repr = str(settings)
            assert "test_user" in str_repr
            assert "secret_password" not in str_repr
            assert "bolt://test:7687" in str_repr


class TestGetSettings:
    """Test cases for get_settings function."""

    def test_get_settings_returns_singleton(self):
        """Test that get_settings returns the same instance."""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "bolt://test:7687",
                "NEO4J_USERNAME": "test_user",
                "NEO4J_PASSWORD": "test_pass",
            },
            clear=True,
        ):
            # Clear cached settings
            if hasattr(get_settings, "_settings"):
                delattr(get_settings, "_settings")

            settings1 = get_settings()
            settings2 = get_settings()

            assert settings1 is settings2
            assert settings1.neo4j_username == "test_user"

    def test_get_settings_creates_new_instance_if_none(self):
        """Test that get_settings creates new instance if none exists."""
        with patch.dict(
            os.environ,
            {
                "NEO4J_URI": "bolt://test:7687",
                "NEO4J_USERNAME": "test_user",
                "NEO4J_PASSWORD": "test_pass",
            },
            clear=True,
        ):
            # Clear cached settings
            if hasattr(get_settings, "_settings"):
                delattr(get_settings, "_settings")

            settings = get_settings()
            assert settings.neo4j_username == "test_user"
            assert settings.neo4j_uri == "bolt://test:7687"
