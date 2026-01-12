"""
Integration tests for GraphRAG application.

Tests end-to-end workflows, component integration,
and real-world usage scenarios.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from config.settings import get_settings
from data.processor import DataProcessor
from graph.neo4j_client import create_neo4j_client


class TestConfigIntegration:
    """Integration tests for configuration module."""

    def test_settings_with_real_env_vars(self):
        """Test settings with actual environment variables."""
        # This test requires environment variables to be set
        # It will be skipped in CI unless they are provided
        if not all(
            [
                os.getenv("NEO4J_URI"),
                os.getenv("NEO4J_USERNAME"),
                os.getenv("NEO4J_PASSWORD"),
            ]
        ):
            pytest.skip("Missing required Neo4j environment variables")

        settings = get_settings()
        assert settings.neo4j_uri
        assert settings.neo4j_username
        assert settings.neo4j_password


class TestNeo4jClientIntegration:
    """Integration tests for Neo4j client."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_neo4j_connection(self, test_settings):
        """Test connection to real Neo4j database."""
        pytest.skip("Requires actual Neo4j database - run with manual setup")

        # This test would require a real Neo4j instance
        # client = create_neo4j_client()
        # with client:
        #     result = client.query("RETURN 1 as test")
        #     assert result == [{"test": 1}]


class TestDataProcessorIntegration:
    """Integration tests for data processor."""

    def test_real_csv_loading(self):
        """Test loading real CSV data from internet."""
        processor = DataProcessor()

        # This test uses real data from the internet
        # May be slow, so mark as such
        pytest.importorskip("requests")

        try:
            data = processor.load_news_data()
            assert isinstance(data, pd.DataFrame)
            assert len(data) > 0
            assert "title" in data.columns
            assert "text" in data.columns
            assert "date" in data.columns
        except Exception as e:
            pytest.skip(f"Could not load real data: {e}")

    def test_data_processing_pipeline(self, sample_news_data):
        """Test complete data processing pipeline."""
        processor = DataProcessor()

        # Step 1: Validate data
        processor._validate_news_data(sample_news_data)

        # Step 2: Clean data
        cleaned_data = processor.clean_text_data(sample_news_data)
        assert isinstance(cleaned_data, pd.DataFrame)
        assert len(cleaned_data) <= len(sample_news_data)

        # Step 3: Get summary
        summary = processor.get_data_summary(cleaned_data)
        assert isinstance(summary, dict)
        assert "total_articles" in summary
        assert "columns" in summary


class TestApplicationIntegration:
    """Integration tests for complete application flow."""

    @pytest.mark.integration
    def test_application_workflow_mock(self, test_settings, sample_news_data):
        """Test complete application workflow with mocked Neo4j."""
        with patch("data.processor.pd.read_csv") as mock_read_csv:
            mock_read_csv.return_value = sample_news_data

            # Import and run main components
            from main import (
                DataProcessor,
                create_neo4j_client,
                get_settings,
                setup_logger,
            )

            # Get settings
            settings = get_settings()
            assert settings.app_name == "GraphRAG"

            # Setup logging
            logger = setup_logger("test")
            assert logger is not None

            # Process data
            processor = DataProcessor()
            data = processor.load_news_data()
            cleaned_data = processor.clean_text_data(data)
            summary = processor.get_data_summary(cleaned_data)

            assert summary["total_articles"] > 0
            assert isinstance(summary["sample_articles"], list)

    def test_error_handling_integration(self):
        """Test error handling across components."""
        with patch("data.processor.pd.read_csv") as mock_read_csv:
            mock_read_csv.side_effect = Exception("Network error")

            processor = DataProcessor()

            with pytest.raises(SystemExit):
                processor.load_news_data()


class TestPerformanceIntegration:
    """Integration tests for performance scenarios."""

    @pytest.mark.slow
    def test_large_dataset_processing(self):
        """Test processing of large datasets."""
        # Create larger dataset
        large_data = pd.DataFrame(
            {
                "title": [f"Article {i}" for i in range(1000)],
                "date": [f"2024-01-{(i % 30) + 1:02d}" for i in range(1000)],
                "text": [
                    f"This is article {i} with sufficient content for testing purposes."
                    for i in range(1000)
                ],
            }
        )

        processor = DataProcessor()

        # Time the processing
        import time

        start_time = time.time()

        cleaned_data = processor.clean_text_data(large_data)
        summary = processor.get_data_summary(cleaned_data)

        end_time = time.time()
        processing_time = end_time - start_time

        # Assertions
        assert isinstance(cleaned_data, pd.DataFrame)
        assert len(cleaned_data) <= 1000
        assert processing_time < 10.0  # Should process within 10 seconds

        # Should have processed data
        assert summary["total_articles"] > 0
