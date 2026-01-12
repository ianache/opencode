"""
Unit tests for data processor module.

Tests data loading, cleaning, validation,
and preprocessing functions.
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from data.processor import DataProcessor, load_news_data


class TestDataProcessor:
    """Test cases for DataProcessor class."""

    def test_initialization(self, test_settings):
        """Test data processor initialization."""
        processor = DataProcessor()
        assert processor.settings is not None
        assert (
            processor.settings.news_data_url
            == "https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/news_articles.csv"
        )

    @patch("data.processor.pd.read_csv")
    def test_load_news_data_success(
        self, mock_read_csv, test_settings, sample_news_data
    ):
        """Test successful news data loading."""
        # Setup mock
        mock_read_csv.return_value = sample_news_data

        # Test
        processor = DataProcessor()
        result = processor.load_news_data()

        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ["title", "date", "text"]
        mock_read_csv.assert_called_once_with(test_settings.news_data_url)

    @patch("data.processor.pd.read_csv")
    def test_load_news_data_custom_url(self, mock_read_csv, sample_news_data):
        """Test loading news data with custom URL."""
        # Setup mock
        custom_url = "https://example.com/custom_data.csv"
        mock_read_csv.return_value = sample_news_data

        # Test
        processor = DataProcessor()
        result = processor.load_news_data(custom_url)

        # Assertions
        assert isinstance(result, pd.DataFrame)
        mock_read_csv.assert_called_once_with(custom_url)

    @patch("data.processor.pd.read_csv")
    def test_load_news_data_failure(self, mock_read_csv, test_settings):
        """Test news data loading failure."""
        # Setup mock to raise exception
        mock_read_csv.side_effect = Exception("Failed to read CSV")

        # Test
        processor = DataProcessor()
        with pytest.raises(SystemExit) as exc_info:
            processor.load_news_data()

        assert exc_info.value.code == 1

    def test_validate_news_data_success(self, test_settings, sample_news_data):
        """Test successful data validation."""
        processor = DataProcessor()
        # Should not raise any exception
        processor._validate_news_data(sample_news_data)

    def test_validate_news_data_missing_columns(self, test_settings):
        """Test validation with missing required columns."""
        # Create data with missing columns
        invalid_data = pd.DataFrame(
            {
                "title": ["Test Article"],
                "content": ["Test content"],  # Missing 'date' and 'text' columns
            }
        )

        # Test
        processor = DataProcessor()
        with pytest.raises(SystemExit) as exc_info:
            processor._validate_news_data(invalid_data)

        assert exc_info.value.code == 1

    def test_validate_news_data_empty(self, test_settings):
        """Test validation with empty data."""
        # Create empty DataFrame with correct columns
        empty_data = pd.DataFrame(columns=["title", "date", "text"])

        # Test
        processor = DataProcessor()
        with pytest.raises(SystemExit) as exc_info:
            processor._validate_news_data(empty_data)

        assert exc_info.value.code == 1

    def test_clean_text_data_basic(self, test_settings, sample_news_data_with_issues):
        """Test basic text cleaning functionality."""
        processor = DataProcessor()
        result = processor.clean_text_data(sample_news_data_with_issues)

        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert "title" in result.columns
        assert "text" in result.columns

        # Check that missing titles are filled
        assert result["title"].isnull().sum() == 0
        assert "[No Title]" in result["title"].values

        # Check that missing text is filled
        assert result["text"].isnull().sum() == 0

    def test_clean_text_data_removes_short_text(self, test_settings):
        """Test that short text articles are removed."""
        # Create data with short text
        data = pd.DataFrame(
            {
                "title": ["Valid Article", "Short Article", "Another Valid"],
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "text": [
                    "This is valid content with enough length",
                    "Short",
                    "Another valid article with sufficient text",
                ],
            }
        )

        processor = DataProcessor()
        result = processor.clean_text_data(data)

        # Should remove the short article
        assert len(result) == 2
        assert "Short" not in result["text"].values

    def test_clean_text_data_removes_no_content(self, test_settings):
        """Test that '[No Content]' articles are removed."""
        # Create data with no content markers
        data = pd.DataFrame(
            {
                "title": ["Valid Article", "No Content Article", "Another Valid"],
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "text": ["Valid content", "[No Content]", "Another valid content"],
            }
        )

        processor = DataProcessor()
        result = processor.clean_text_data(data)

        # Should remove the no content article
        assert len(result) == 2
        assert "[No Content]" not in result["text"].values

    def test_get_data_summary_success(self, test_settings, sample_news_data):
        """Test successful data summary generation."""
        processor = DataProcessor()
        summary = processor.get_data_summary(sample_news_data)

        # Assertions
        assert isinstance(summary, dict)
        assert "total_articles" in summary
        assert "columns" in summary
        assert "data_types" in summary
        assert "missing_values" in summary
        assert "sample_articles" in summary

        assert summary["total_articles"] == 3
        assert set(summary["columns"]) == {"title", "date", "text"}
        assert len(summary["sample_articles"]) == 3

    def test_get_data_summary_empty(self, test_settings):
        """Test data summary with empty DataFrame."""
        processor = DataProcessor()
        summary = processor.get_data_summary(pd.DataFrame())

        # Should handle empty data gracefully
        assert isinstance(summary, dict)
        assert summary["total_articles"] == 0
        assert summary["sample_articles"] == []

    @patch("data.processor.pd.read_csv")
    def test_clean_text_data_with_exception(self, mock_read_csv, test_settings):
        """Test clean_text_data with exception."""
        # Setup mock that will cause issues
        problematic_data = pd.DataFrame(
            {"title": ["Test"], "date": ["2024-01-01"], "text": ["Valid content"]}
        )

        # Make title column cause an issue
        problematic_data.loc[:, "title"] = None

        processor = DataProcessor()

        with pytest.raises(SystemExit) as exc_info:
            processor.clean_text_data(problematic_data)

        assert exc_info.value.code == 1


class TestLoadNewsData:
    """Test cases for load_news_data function."""

    @patch("data.processor.pd.read_csv")
    def test_load_news_data_function(self, mock_read_csv, sample_news_data):
        """Test load_news_data convenience function."""
        # Setup mock
        mock_read_csv.return_value = sample_news_data

        # Test
        result = load_news_data()

        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    @patch("data.processor.pd.read_csv")
    def test_load_news_data_function_with_url(self, mock_read_csv, sample_news_data):
        """Test load_news_data function with custom URL."""
        # Setup mock
        custom_url = "https://example.com/custom.csv"
        mock_read_csv.return_value = sample_news_data

        # Test
        result = load_news_data(custom_url)

        # Assertions
        assert isinstance(result, pd.DataFrame)
        mock_read_csv.assert_called_once_with(custom_url)
