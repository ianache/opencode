"""
Graph database module for GraphRAG application.

Handles Neo4j connections, graph operations,
and schema management using langchain-neo4j.
"""

from .neo4j_client import Neo4jClient, create_neo4j_client
from .product_manager import ProductManager

__all__ = ["Neo4jClient", "create_neo4j_client", "ProductManager"]
