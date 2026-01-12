"""
Neo4j client for GraphRAG application.

Handles Neo4j database connections, query execution,
and graph operations using langchain-neo4j.
"""

import sys
from typing import Any, Dict, List, Optional

from langchain_neo4j import Neo4jGraph

from config.settings import get_settings


class Neo4jClient:
    """Neo4j database client wrapper."""

    def __init__(self):
        self.settings = get_settings()
        self._graph: Optional[Neo4jGraph] = None
        self._is_connected = False

    def connect(self) -> None:
        """Establish connection to Neo4j database."""
        try:
            self._graph = Neo4jGraph(
                url=self.settings.neo4j_uri,
                username=self.settings.neo4j_username,
                password=self.settings.neo4j_password,
                database=self.settings.neo4j_database,
                refresh_schema=False,
            )

            # Test the connection
            self._graph.query("RETURN 1 as test")
            self._is_connected = True
            print("Successfully connected to Neo4j database")

        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            sys.exit(1)

    @property
    def graph(self) -> Neo4jGraph:
        """Get Neo4j graph instance, connecting if necessary."""
        if not self._is_connected or self._graph is None:
            self.connect()
        return self._graph  # type: ignore

    def query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        try:
            return self.graph.query(query, params=params or {})
        except Exception as e:
            print(f"Error executing query: {query}")
            print(f"Error details: {e}")
            raise

    def get_schema(self) -> str:
        """Get the database schema."""
        try:
            return self.graph.get_schema
        except Exception as e:
            print(f"Error getting schema: {e}")
            raise

    def refresh_schema(self) -> None:
        """Refresh the database schema."""
        try:
            self.graph.refresh_schema()
        except Exception as e:
            print(f"Error refreshing schema: {e}")
            raise

    def close(self) -> None:
        """Close the database connection."""
        try:
            if self._graph and hasattr(self._graph, "close"):
                self._graph.close()
            self._is_connected = False
            print("Neo4j connection closed")
        except Exception as e:
            print(f"Error closing connection: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_neo4j_client() -> Neo4jClient:
    """Create and return a new Neo4jClient instance."""
    return Neo4jClient()
