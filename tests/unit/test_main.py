"""
Unit tests for main application.

Tests main entry point, application flow,
and integration of all components.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from main import main


class TestMainApplication:
    """Test cases for main application."""

    @patch("main.DataProcessor")
    @patch("main.create_neo4j_client")
    @patch("main.setup_logger")
    @patch("main.get_settings")
    def test_main_success_flow(
        self,
        mock_get_settings,
        mock_setup_logger,
        mock_create_client,
        mock_data_processor,
        sample_news_data,
        test_settings,
    ):
        """Test successful main application flow."""
        # Setup mocks
        mock_get_settings.return_value = test_settings
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger

        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get_schema.return_value = "Test schema"
        mock_create_client.return_value = mock_client

        mock_processor_instance = Mock()
        mock_processor_instance.load_news_data.return_value = sample_news_data
        mock_processor_instance.clean_text_data.return_value = sample_news_data
        mock_processor_instance.get_data_summary.return_value = {
            "total_articles": 3,
            "columns": ["title", "date", "text"],
            "missing_values": {},
            "sample_articles": sample_news_data.head(3).to_dict("records"),
        }
        mock_data_processor.return_value = mock_processor_instance

        # Test main function
        main()

        # Assertions
        mock_get_settings.assert_called_once()
        mock_setup_logger.assert_called_once_with("graphrag")
        mock_create_client.assert_called_once()
        mock_data_processor.assert_called_once()
        mock_processor_instance.load_news_data.assert_called_once()
        mock_processor_instance.clean_text_data.assert_called_once_with(
            sample_news_data
        )
        mock_processor_instance.get_data_summary.assert_called_once()
        mock_logger.info.assert_called()

    @patch("main.DataProcessor")
    @patch("main.create_neo4j_client")
    @patch("main.setup_logger")
    @patch("main.get_settings")
    def test_main_with_keyboard_interrupt(
        self,
        mock_get_settings,
        mock_setup_logger,
        mock_create_client,
        mock_data_processor,
        test_settings,
    ):
        """Test main application with keyboard interrupt."""
        # Setup mocks
        mock_get_settings.return_value = test_settings
        mock_setup_logger.return_value = Mock()

        mock_create_client.side_effect = KeyboardInterrupt("User interrupt")

        # Test main function
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    @patch("main.DataProcessor")
    @patch("main.create_neo4j_client")
    @patch("main.setup_logger")
    @patch("main.get_settings")
    def test_main_with_exception(
        self,
        mock_get_settings,
        mock_setup_logger,
        mock_create_client,
        mock_data_processor,
        test_settings,
    ):
        """Test main application with general exception."""
        # Setup mocks
        mock_get_settings.return_value = test_settings
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger

        mock_create_client.side_effect = Exception("Test error")

        # Test main function
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_logger.error.assert_called_once()

    @patch("main.DataProcessor")
    @patch("main.create_neo4j_client")
    @patch("main.setup_logger")
    @patch("main.get_settings")
    def test_main_schema_retrieval_failure(
        self,
        mock_get_settings,
        mock_setup_logger,
        mock_create_client,
        mock_data_processor,
        sample_news_data,
        test_settings,
    ):
        """Test main application when schema retrieval fails."""
        # Setup mocks
        mock_get_settings.return_value = test_settings
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger

        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get_schema.side_effect = Exception("Schema error")
        mock_create_client.return_value = mock_client

        mock_processor_instance = Mock()
        mock_processor_instance.load_news_data.return_value = sample_news_data
        mock_processor_instance.clean_text_data.return_value = sample_news_data
        mock_processor_instance.get_data_summary.return_value = {
            "total_articles": 3,
            "columns": ["title", "date", "text"],
            "missing_values": {},
            "sample_articles": sample_news_data.head(3).to_dict("records"),
        }
        mock_data_processor.return_value = mock_processor_instance

        # Test main function - should handle schema error gracefully
        main()

        # Assertions
        mock_logger.warning.assert_called()
        mock_processor_instance.load_news_data.assert_called_once()
