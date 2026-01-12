"""
Data processing module for GraphRAG application.

Handles data loading, cleaning, validation,
and preprocessing for news article data.
"""

from .processor import DataProcessor, load_news_data

__all__ = ["DataProcessor", "load_news_data"]
