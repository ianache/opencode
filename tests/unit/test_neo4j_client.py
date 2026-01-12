"""
Unit tests for Neo4j client module.

Tests database connection, query execution,
and error handling.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from graph.neo4j_client import Neo4jClient, create_neo4j_client


class TestNeo4jClient:
    """Test cases for Neo4jClient class."""

    def test_initialization(self, test_settings):
        """Test client initialization."""
        client = Neo4jClient()
        assert client.settings is not None
        assert client._graph is None
        assert client._is_connected is False

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_connect_success(self, mock_neo4j_graph, test_settings):
        """Test successful database connection."""
        # Setup mock
        mock_graph_instance = Mock()
        mock_graph_instance.query.return_value = [{"test": 1}]
        mock_neo4j_graph.return_value = mock_graph_instance

        # Test connection
        client = Neo4jClient()
        client.connect()

        # Assertions
        assert client._is_connected is True
        assert client._graph is mock_graph_instance
        mock_neo4j_graph.assert_called_once_with(
            url=test_settings.neo4j_uri,
            username=test_settings.neo4j_username,
            password=test_settings.neo4j_password,
            database=test_settings.neo4j_database,
            refresh_schema=False,
        )
        mock_graph_instance.query.assert_called_once_with("RETURN 1 as test")

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_connect_failure(self, mock_neo4j_graph, test_settings):
        """Test database connection failure."""
        # Setup mock to raise exception
        mock_neo4j_graph.side_effect = Exception("Connection failed")

        # Test connection
        with pytest.raises(SystemExit) as exc_info:
            client = Neo4jClient()
            client.connect()

        assert exc_info.value.code == 1
        assert client._is_connected is False

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_graph_property_connects_if_needed(self, mock_neo4j_graph, test_settings):
        """Test that graph property connects if not already connected."""
        # Setup mock
        mock_graph_instance = Mock()
        mock_graph_instance.query.return_value = [{"test": 1}]
        mock_neo4j_graph.return_value = mock_graph_instance

        # Test graph property
        client = Neo4jClient()
        graph = client.graph

        # Assertions
        assert graph is mock_graph_instance
        assert client._is_connected is True
        mock_neo4j_graph.assert_called_once()

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_graph_property_uses_existing_connection(
        self, mock_neo4j_graph, test_settings
    ):
        """Test that graph property uses existing connection."""
        # Setup mock
        mock_graph_instance = Mock()
        mock_graph_instance.query.return_value = [{"test": 1}]
        mock_neo4j_graph.return_value = mock_graph_instance

        # Test
        client = Neo4jClient()
        client.connect()  # Connect first
        graph1 = client.graph
        graph2 = client.graph  # Get graph again

        # Assertions
        assert graph1 is graph2
        assert mock_neo4j_graph.call_count == 1  # Only called once

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_query_success(self, mock_neo4j_graph, test_settings):
        """Test successful query execution."""
        # Setup mock
        mock_graph_instance = Mock()
        mock_graph_instance.query.return_value = [{"result": "data"}]
        mock_neo4j_graph.return_value = mock_graph_instance

        # Test query
        client = Neo4jClient()
        client.connect()
        result = client.query("MATCH (n) RETURN n")

        # Assertions
        assert result == [{"result": "data"}]
        mock_graph_instance.query.assert_called_with("MATCH (n) RETURN n", params={})

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_query_with_params(self, mock_neo4j_graph, test_settings):
        """Test query execution with parameters."""
        # Setup mock
        mock_graph_instance = Mock()
        mock_graph_instance.query.return_value = [{"result": "data"}]
        mock_neo4j_graph.return_value = mock_graph_instance

        # Test query
        client = Neo4jClient()
        client.connect()
        result = client.query(
            "MATCH (n) WHERE n.name = $name RETURN n", {"name": "test"}
        )

        # Assertions
        assert result == [{"result": "data"}]
        mock_graph_instance.query.assert_called_with(
            "MATCH (n) WHERE n.name = $name RETURN n", params={"name": "test"}
        )

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_query_failure(self, mock_neo4j_graph, test_settings):
        """Test query execution failure."""
        # Setup mock
        mock_graph_instance = Mock()
        mock_graph_instance.query.side_effect = Exception("Query failed")
        mock_neo4j_graph.return_value = mock_graph_instance

        # Test query
        client = Neo4jClient()
        client.connect()

        with pytest.raises(Exception, match="Query failed"):
            client.query("INVALID QUERY")

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_get_schema(self, mock_neo4j_graph, test_settings):
        """Test getting database schema."""
        # Setup mock
        mock_graph_instance = Mock()
        mock_graph_instance.get_schema = "Test schema"
        mock_neo4j_graph.return_value = mock_graph_instance

        # Test
        client = Neo4jClient()
        client.connect()
        schema = client.get_schema()

        # Assertions
        assert schema == "Test schema"

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_refresh_schema(self, mock_neo4j_graph, test_settings):
        """Test refreshing database schema."""
        # Setup mock
        mock_graph_instance = Mock()
        mock_neo4j_graph.return_value = mock_graph_instance

        # Test
        client = Neo4jClient()
        client.connect()
        client.refresh_schema()

        # Assertions
        mock_graph_instance.refresh_schema.assert_called_once()

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_context_manager(self, mock_neo4j_graph, test_settings):
        """Test context manager functionality."""
        # Setup mock
        mock_graph_instance = Mock()
        mock_neo4j_graph.return_value = mock_graph_instance

        # Test context manager
        with Neo4jClient() as client:
            client.connect()
            assert client._is_connected is True

        # After context exit
        # Note: close() might not be called if Neo4jGraph doesn't have close method
        # This test verifies the context manager pattern works

    @patch("graph.neo4j_client.Neo4jGraph")
    def test_close(self, mock_neo4j_graph, test_settings):
        """Test closing database connection."""
        # Setup mock
        mock_graph_instance = Mock()
        mock_graph_instance.close = Mock()
        mock_neo4j_graph.return_value = mock_graph_instance

        # Test close
        client = Neo4jClient()
        client.connect()
        client.close()

        # Assertions
        assert client._is_connected is False
        mock_graph_instance.close.assert_called_once()


class TestCreateNeo4jClient:
    """Test cases for create_neo4j_client function."""

    def test_create_neo4j_client(self):
        """Test Neo4jClient creation function."""
        client = create_neo4j_client()
        assert isinstance(client, Neo4jClient)
        assert client._graph is None
        assert client._is_connected is False
