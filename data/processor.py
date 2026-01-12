"""
Data processor for GraphRAG application.

Handles data loading, cleaning, validation,
and preprocessing for news article data.
"""

from pathlib import Path
from typing import Optional

import pandas as pd

from config.settings import get_settings


class DataProcessingError(Exception):
    """Raised when data processing operations fail."""

    pass


class DataProcessor:
    """Data processor for news articles."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def load_news_data(self, url: Optional[str] = None) -> pd.DataFrame:
        """Load news data from CSV URL."""
        try:
            data_url = url or self.settings.news_data_url
            print(f"Loading news data from: {data_url}")

            news = pd.read_csv(data_url)
            print(f"Successfully loaded {len(news)} news articles")

            # Validate the data structure
            self._validate_news_data(news)

            return news

        except Exception as e:
            print(f"Error loading news data: {e}")
            raise DataProcessingError(f"Failed to load news data: {e}")

    def _validate_news_data(self, df: pd.DataFrame) -> None:
        """Validate that news data has expected structure."""
        required_columns = ["title", "date", "text"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            error_msg = (
                f"News data missing required columns: {', '.join(missing_columns)}"
            )
            print(f"Error: {error_msg}")
            print(f"Available columns: {list(df.columns)}")
            raise DataProcessingError(error_msg)

        if len(df) == 0:
            raise DataProcessingError("News data is empty")

        print(f"Data validation passed: {len(df)} rows, {len(df.columns)} columns")

    def clean_text_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess text data."""
        try:
            # Make a copy to avoid SettingWithCopyWarning
            cleaned_df = df.copy()

            # Basic text cleaning
            cleaned_df["title"] = cleaned_df["title"].astype(str).str.strip()
            cleaned_df["text"] = cleaned_df["text"].astype(str).str.strip()

            # Handle missing values
            cleaned_df["title"] = cleaned_df["title"].fillna("[No Title]")
            cleaned_df["text"] = cleaned_df["text"].fillna("[No Content]")

            # Filter out articles with insufficient text content
            text_length_mask = cleaned_df["text"].str.len() > 10
            content_mask = cleaned_df["text"] != "[No Content]"
            empty_mask = cleaned_df["text"] != ""

            combined_mask = text_length_mask & content_mask & empty_mask
            result_df = cleaned_df[combined_mask].copy()

            print(f"Text cleaning completed: {len(result_df)} articles remain")
            return result_df

        except Exception as e:
            print(f"Error cleaning text data: {e}")
            raise DataProcessingError(f"Failed to clean text data: {e}")

    def get_data_summary(self, df: pd.DataFrame) -> dict:
        """Get summary statistics for data."""
        try:
            summary = {
                "total_articles": len(df),
                "columns": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "sample_articles": df.head(3).to_dict("records") if len(df) > 0 else [],
            }
            return summary
        except Exception as e:
            print(f"Error generating data summary: {e}")
            return {}


def load_news_data(url: Optional[str] = None) -> pd.DataFrame:
    """Convenience function to load news data."""
    processor = DataProcessor()
    return processor.load_news_data(url)
