"""
Unit tests for ProductManager module.

Tests product management functionality including CRUD operations,
relationships, and business queries.
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from graph.neo4j_client import Neo4jClient
from graph.product_manager import ProductManager


class TestProductManager:
    """Test cases for ProductManager class."""

    def test_initialization(self, test_settings):
        """Test ProductManager initialization."""
        mock_client = Mock(spec=Neo4jClient)
        product_manager = ProductManager(mock_client)
        assert product_manager.client == mock_client

    @patch("graph.product_manager.logger")
    def test_create_product_success(self, mock_logger, test_settings):
        """Test successful product creation."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [
            {"p": {"code": "TEST", "name": "Test Product"}}
        ]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.create_product("TEST", "Test Product")

        # Assertions
        assert result == {"code": "TEST", "name": "Test Product"}
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        assert "MERGE (p:Product {code: $code})" in call_args[0][0]
        # Check parameters regardless of whitespace in query
        params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
        assert params["code"] == "TEST"
        assert params["name"] == "Test Product"

    @patch("graph.product_manager.logger")
    def test_create_product_failure(self, mock_logger, test_settings):
        """Test product creation failure."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = []

        # Test
        product_manager = ProductManager(mock_client)
        with pytest.raises(Exception, match="Failed to create product"):
            product_manager.create_product("TEST", "Test Product")

    @patch("graph.product_manager.logger")
    def test_get_product_success(self, mock_logger, test_settings):
        """Test successful product retrieval."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [
            {"p": {"code": "TEST", "name": "Test Product"}}
        ]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.get_product("TEST")

        # Assertions
        assert result == {"code": "TEST", "name": "Test Product"}
        # Check that query was called with correct parameters (flexible on formatting)
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        # Extract the actual query and parameters
        actual_query = call_args[0][0] if call_args[0] else ""
        actual_params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
        assert "MATCH (p:Product {code: $code})" in actual_query
        assert actual_params["code"] == "TEST"

    @patch("graph.product_manager.logger")
    def test_get_product_not_found(self, mock_logger, test_settings):
        """Test product retrieval when not found."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = []

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.get_product("NONEXISTENT")

        # Assertions
        assert result is None

    @patch("graph.product_manager.logger")
    def test_update_product_success(self, mock_logger, test_settings):
        """Test successful product update."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [
            {"p": {"code": "TEST", "name": "Updated Name"}}
        ]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.update_product("TEST", name="Updated Name")

        # Assertions
        assert result is True
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        actual_query = call_args[0][0] if call_args[0] else ""
        actual_params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
        assert "MATCH (p:Product {code: $code})" in actual_query
        assert actual_params["code"] == "TEST"
        assert actual_params["name"] == "Updated Name"

    @patch("graph.product_manager.logger")
    def test_update_product_no_kwargs(self, mock_logger, test_settings):
        """Test product update with no parameters."""
        mock_client = Mock(spec=Neo4jClient)
        product_manager = ProductManager(mock_client)
        result = product_manager.update_product("TEST")
        assert result is False
        mock_client.query.assert_not_called()

    @patch("graph.product_manager.logger")
    def test_delete_product_success(self, mock_logger, test_settings):
        """Test successful product deletion."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [{"deleted": 1}]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.delete_product("TEST")

        # Assertions
        assert result is True
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        actual_query = call_args[0][0] if call_args[0] else ""
        actual_params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
        assert "MATCH (p:Product {code: $code})" in actual_query
        assert "DETACH DELETE p" in actual_query
        assert actual_params["code"] == "TEST"

    @patch("graph.product_manager.logger")
    def test_delete_product_not_found(self, mock_logger, test_settings):
        """Test product deletion when not found."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [{"deleted": 0}]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.delete_product("NONEXISTENT")

        # Assertions
        assert result is False

    @patch("graph.product_manager.logger")
    def test_list_all_products(self, mock_logger, test_settings):
        """Test listing all products."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [
            {"p": {"code": "P1", "name": "Product 1"}},
            {"p": {"code": "P2", "name": "Product 2"}},
        ]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.list_all_products()

        # Assertions
        assert len(result) == 2
        assert result[0] == {"code": "P1", "name": "Product 1"}
        assert result[1] == {"code": "P2", "name": "Product 2"}

    @patch("graph.product_manager.logger")
    def test_create_functionality_success(self, mock_logger, test_settings):
        """Test successful functionality creation."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [
            {"f": {"code": "FUNC1", "name": "Test Functionality"}}
        ]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.create_functionality("FUNC1", "Test Functionality")

        # Assertions
        assert result == {"code": "FUNC1", "name": "Test Functionality"}
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        assert "MERGE (f:Functionality {code: $code})" in call_args[0][0]

    @patch("graph.product_manager.logger")
    def test_create_component_success(self, mock_logger, test_settings):
        """Test successful component creation."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [
            {"c": {"code": "COMP1", "name": "Test Component"}}
        ]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.create_component("COMP1", "Test Component")

        # Assertions
        assert result == {"code": "COMP1", "name": "Test Component"}
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        assert "MERGE (c:Component {code: $code})" in call_args[0][0]

    @patch("graph.product_manager.logger")
    def test_create_incident_success(self, mock_logger, test_settings):
        """Test successful incident creation."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [
            {"i": {"code": "INC1", "description": "Test Incident"}}
        ]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.create_incident(
            "INC1", "Test Incident", "SLA_HIGH", "FUNC1"
        )

        # Assertions
        assert result == {"code": "INC1", "description": "Test Incident"}
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        actual_query = call_args[0][0] if call_args[0] else ""
        actual_params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
        assert "MERGE (i:Incident {code: $code})" in actual_query
        assert actual_params["functionality_code"] == "FUNC1"

    @patch("graph.product_manager.logger")
    def test_create_incident_functionality_not_found(self, mock_logger, test_settings):
        """Test incident creation when functionality not found."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = []

        # Test
        product_manager = ProductManager(mock_client)
        with pytest.raises(
            Exception, match="Failed to create incident - functionality not found"
        ):
            product_manager.create_incident(
                "INC1", "Test Incident", "SLA_HIGH", "NONEXISTENT"
            )

    @patch("graph.product_manager.logger")
    def test_create_resolution_success(self, mock_logger, test_settings):
        """Test successful resolution creation."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [
            {"r": {"incident_code": "INC1", "procedure": "Test Procedure"}}
        ]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.create_resolution(
            "INC1", "2024-01-15T10:30:00Z", "Test Procedure"
        )

        # Assertions
        assert result == {"incident_code": "INC1", "procedure": "Test Procedure"}
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        assert "MERGE (r:Resolution {incident_code: $incident_code})" in call_args[0][0]

    @patch("graph.product_manager.logger")
    def test_assign_functionality_to_product_success(self, mock_logger, test_settings):
        """Test successful functionality assignment to product."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [{"r": {"created_at": datetime.now()}}]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.assign_functionality_to_product("PROD1", "FUNC1")

        # Assertions
        assert result is True
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        actual_query = call_args[0][0] if call_args[0] else ""
        actual_params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
        assert "MERGE (p)-[r:ASIGNACION_FUNCIONALIDAD]->(f)" in actual_query
        assert actual_params["product_code"] == "PROD1"
        assert actual_params["functionality_code"] == "FUNC1"

    @patch("graph.product_manager.logger")
    def test_assign_functionality_to_component_success(
        self, mock_logger, test_settings
    ):
        """Test successful functionality assignment to component."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [{"r": {"created_at": datetime.now()}}]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.assign_functionality_to_component("COMP1", "FUNC1")

        # Assertions
        assert result is True
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        assert "MERGE (c)-[r:ASIGNACION_FUNCIONALIDAD]->(f)" in call_args[0][0]

    @patch("graph.product_manager.logger")
    def test_get_product_with_functionalities(self, mock_logger, test_settings):
        """Test getting product with functionalities."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [
            {
                "p": {"code": "PROD1", "name": "Test Product"},
                "functionalities": [{"code": "FUNC1", "name": "Functionality 1"}],
                "incidents": [],
                "resolutions": [],
            }
        ]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.get_product_with_functionalities("PROD1")

        # Assertions
        assert result["p"]["code"] == "PROD1"
        assert len(result["functionalities"]) == 1
        assert result["functionalities"][0]["code"] == "FUNC1"

    @patch("graph.product_manager.logger")
    def test_get_all_products_summary(self, mock_logger, test_settings):
        """Test getting all products summary."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [
            {
                "product_code": "PROD1",
                "product_name": "Product 1",
                "functionality_count": 3,
                "incident_count": 1,
            },
            {
                "product_code": "PROD2",
                "product_name": "Product 2",
                "functionality_count": 2,
                "incident_count": 0,
            },
        ]

        # Test
        product_manager = ProductManager(mock_client)
        result = product_manager.get_all_products_summary()

        # Assertions
        assert len(result) == 2
        assert result[0]["product_code"] == "PROD1"
        assert result[0]["functionality_count"] == 3
        assert result[1]["product_code"] == "PROD2"
        assert result[1]["incident_count"] == 0

    @patch("graph.product_manager.logger")
    def test_create_constraints(self, mock_logger, test_settings):
        """Test creating database constraints."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)

        # Test
        product_manager = ProductManager(mock_client)
        product_manager.create_constraints()

        # Assertions
        assert mock_client.query.call_count == 5  # 5 constraints

        # Check that constraint queries were called
        calls = [call[0][0] for call in mock_client.query.call_args_list]
        assert any("product_code_unique" in call for call in calls)
        assert any("functionality_code_unique" in call for call in calls)
        assert any("component_code_unique" in call for call in calls)
        assert any("incident_code_unique" in call for call in calls)
        assert any("resolution_incident_unique" in call for call in calls)


class TestProductManagerErrorHandling:
    """Test cases for ProductManager error handling."""

    @patch("graph.product_manager.logger")
    def test_query_exception_propagation(self, mock_logger, test_settings):
        """Test that database exceptions are properly propagated."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.side_effect = Exception("Database error")

        # Test
        product_manager = ProductManager(mock_client)

        with pytest.raises(Exception, match="Database error"):
            product_manager.create_product("TEST", "Test Product")

        # Verify error was logged
        mock_logger.error.assert_called_once()

    @patch("graph.product_manager.logger")
    def test_incident_creation_invalid_date(self, mock_logger, test_settings):
        """Test resolution creation with invalid date."""
        # Setup mock
        mock_client = Mock(spec=Neo4jClient)
        mock_client.query.return_value = [{"r": {"incident_code": "INC1"}}]

        # Test with invalid date - should use current date
        product_manager = ProductManager(mock_client)
        result = product_manager.create_resolution(
            "INC1", "invalid-date", "Test Procedure"
        )

        # Should still succeed but use current date
        assert result == {"incident_code": "INC1"}
        mock_client.query.assert_called_once()
