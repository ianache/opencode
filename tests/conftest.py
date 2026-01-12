"""
Pytest configuration and fixtures for GraphRAG application.

Provides common fixtures, test configurations,
and test utilities for all test modules.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings, get_settings
from data.processor import DataProcessor
from graph.neo4j_client import Neo4jClient


@pytest.fixture
def test_settings():
    """Test settings fixture with mock environment variables."""
    # Clear existing environment variables first
    original_env = {}
    for key in [
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "NEO4J_DATABASE",
        "LOG_LEVEL",
    ]:
        if key in os.environ:
            original_env[key] = os.environ[key]
            del os.environ[key]

    # Set up test environment variables
    os.environ.update(
        {
            "NEO4J_URI": "bolt://localhost:7687",
            "NEO4J_USERNAME": "test_user",
            "NEO4J_PASSWORD": "test_password",
            "NEO4J_DATABASE": "test_db",
            "LOG_LEVEL": "DEBUG",
        }
    )

    # Force settings reload
    if hasattr(get_settings, "_settings"):
        delattr(get_settings, "_settings")

    yield get_settings()

    # Cleanup: restore original environment
    for key in [
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "NEO4J_DATABASE",
        "LOG_LEVEL",
    ]:
        if key in os.environ:
            del os.environ[key]

    os.environ.update(original_env)


@pytest.fixture
def mock_neo4j_graph():
    """Mock Neo4j graph fixture."""
    mock_graph = Mock()
    mock_graph.query.return_value = [{"test": "data"}]
    mock_graph.get_schema = "Test schema"
    mock_graph.refresh_schema.return_value = None
    return mock_graph


@pytest.fixture
def sample_news_data():
    """Sample news data fixture for testing."""
    return pd.DataFrame(
        {
            "title": ["Test Article 1", "Test Article 2", "Test Article 3"],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "text": [
                "This is a test article about technology and innovation.",
                "Another test article discussing current events.",
                "A third test article with more content to test processing.",
            ],
        }
    )


@pytest.fixture
def sample_news_data_with_issues():
    """Sample news data with issues for testing validation."""
    return pd.DataFrame(
        {
            "title": [
                "Valid Article",
                None,  # Missing title
                "Another Valid Article",
            ],
            "date": [
                "2024-01-01",
                "2024-01-02",
                None,  # Missing date
            ],
            "text": [
                "Valid content here.",
                "",  # Empty text
                "More valid content for testing.",
            ],
        }
    )


@pytest.fixture
def mock_neo4j_client(mock_neo4j_graph):
    """Mock Neo4j client fixture."""
    client = Neo4jClient()
    client._graph = mock_neo4j_graph
    client._is_connected = True
    return client


@pytest.fixture
def data_processor():
    """Data processor fixture."""
    return DataProcessor()


@pytest.fixture(autouse=True)
def reset_settings():
    """Reset settings between tests."""
    yield
    # Cleanup after test
    if hasattr(get_settings, "_settings"):
        delattr(get_settings, "_settings")


@pytest.fixture
def temp_data_dir(tmp_path):
    """Temporary data directory fixture."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_csv_file(temp_data_dir, sample_news_data):
    """Create a temporary CSV file with sample data."""
    csv_path = temp_data_dir / "sample_news.csv"
    sample_news_data.to_csv(csv_path, index=False)
    return csv_path
