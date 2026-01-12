"""
Test the MCP server tools and functionality.
"""

import pytest
from unittest.mock import Mock, patch

from mcp_server.tools.product_tools import ProductTools
from mcp_server.tools.functionality_tools import FunctionalityTools


class TestProductTools:
    """Test ProductTools functionality."""

    @pytest.fixture
    def mock_product_manager(self):
        """Create a mock ProductManager."""
        return Mock()

    @pytest.fixture
    def product_tools(self, mock_product_manager):
        """Create ProductTools with mocked dependencies."""
        tools = ProductTools()
        tools._product_manager = mock_product_manager
        return tools

    @pytest.fixture
    def mock_context(self):
        """Create a mock MCP Context."""
        return Mock()

    def test_register_product_success(
        self, product_tools, mock_product_manager, mock_context
    ):
        """Test successful product registration."""
        # Setup mock response
        mock_product_manager.create_product.return_value = {
            "code": "TEST",
            "name": "Test Product",
            "created_at": "2024-01-01",
        }
        mock_product_manager.get_functionality.return_value = {
            "code": "FUNC1",
            "name": "Test Functionality",
        }
        mock_product_manager.assign_functionality_to_product.return_value = True
        mock_product_manager.get_product_with_functionalities.return_value = {
            "p": {"code": "TEST", "name": "Test Product"},
            "functionalities": [{"code": "FUNC1", "name": "Test Functionality"}],
            "incidents": [],
            "resolutions": [],
        }

        # Execute test
        result = product_tools.register_product(
            mock_context, "TEST", "Test Product", ["FUNC1"]
        )

        # Verify result
        assert result["success"] is True
        assert result["product"]["code"] == "TEST"
        assert result["product"]["name"] == "Test Product"
        assert len(result["product"]["functionalities"]) == 1

        # Verify method calls
        mock_product_manager.create_product.assert_called_once_with(
            "TEST", "Test Product"
        )
        mock_product_manager.assign_functionality_to_product.assert_called_once_with(
            "TEST", "FUNC1"
        )

    def test_register_product_validation_error(self, product_tools, mock_context):
        """Test product registration with validation error."""
        with pytest.raises(Exception) as exc_info:
            product_tools.register_product(mock_context, "", "Test Product")

        assert "required" in str(exc_info.value).lower()

    def test_get_product_details_success(
        self, product_tools, mock_product_manager, mock_context
    ):
        """Test successful product details retrieval."""
        # Setup mock response
        mock_product_manager.get_product_with_functionalities.return_value = {
            "p": {"code": "TEST", "name": "Test Product"},
            "functionalities": [{"code": "FUNC1", "name": "Test Functionality"}],
            "incidents": [{"code": "INC1", "description": "Test Incident"}],
            "resolutions": [{"incident_code": "INC1", "procedure": "Test Resolution"}],
        }

        # Execute test
        result = product_tools.get_product_details(mock_context, "TEST")

        # Verify result
        assert result["success"] is True
        assert result["product"]["code"] == "TEST"
        assert len(result["functionalities"]) == 1
        assert len(result["incidents"]) == 1
        assert len(result["resolutions"]) == 1

    def test_get_product_details_not_found(
        self, product_tools, mock_product_manager, mock_context
    ):
        """Test product details for non-existent product."""
        # Setup mock response
        mock_product_manager.get_product_with_functionalities.return_value = {}

        # Execute test and expect error
        with pytest.raises(Exception) as exc_info:
            product_tools.get_product_details(mock_context, "NONEXISTENT")

        assert "not found" in str(exc_info.value).lower()


class TestFunctionalityTools:
    """Test FunctionalityTools functionality."""

    @pytest.fixture
    def mock_product_manager(self):
        """Create a mock ProductManager."""
        return Mock()

    @pytest.fixture
    def functionality_tools(self, mock_product_manager):
        """Create FunctionalityTools with mocked dependencies."""
        tools = FunctionalityTools()
        tools._product_manager = mock_product_manager
        return tools

    @pytest.fixture
    def mock_context(self):
        """Create a mock MCP Context."""
        return Mock()

    def test_register_functionality_success(
        self, functionality_tools, mock_product_manager, mock_context
    ):
        """Test successful functionality registration."""
        # Setup mock response
        mock_product_manager.create_functionality.return_value = {
            "code": "FUNC1",
            "name": "Test Functionality",
            "created_at": "2024-01-01",
        }

        # Execute test
        result = functionality_tools.register_functionality(
            mock_context, "FUNC1", "Test Functionality"
        )

        # Verify result
        assert result["success"] is True
        assert result["functionality"]["code"] == "FUNC1"
        assert result["functionality"]["name"] == "Test Functionality"

        # Verify method calls
        mock_product_manager.create_functionality.assert_called_once_with(
            "FUNC1", "Test Functionality"
        )

    def test_assign_functionalities_success(
        self, functionality_tools, mock_product_manager, mock_context
    ):
        """Test successful functionality assignment."""
        # Setup mock responses
        mock_product_manager.get_product.return_value = {"code": "PROD1"}
        mock_product_manager.get_functionality.return_value = {"code": "FUNC1"}
        mock_product_manager.assign_functionality_to_product.return_value = True

        # Execute test
        result = functionality_tools.assign_functionalities_to_product(
            mock_context, "PROD1", ["FUNC1"]
        )

        # Verify result
        assert result["success"] is True
        assert len(result["successful_assignments"]) == 1
        assert result["successful_assignments"][0]["functionality_code"] == "FUNC1"
        assert result["summary"]["successful"] == 1
        assert result["summary"]["total_requested"] == 1

    def test_assign_functionalities_product_not_found(
        self, functionality_tools, mock_product_manager, mock_context
    ):
        """Test functionality assignment to non-existent product."""
        # Setup mock response
        mock_product_manager.get_product.return_value = None

        # Execute test and expect error
        with pytest.raises(Exception) as exc_info:
            functionality_tools.assign_functionalities_to_product(
                mock_context, "NONEXISTENT", ["FUNC1"]
            )

        assert "not found" in str(exc_info.value).lower()


class TestMCPIntegration:
    """Integration tests for MCP server components."""

    @pytest.fixture
    def mock_neo4j_client(self):
        """Create a mock Neo4j client."""
        return Mock()

    def test_complete_workflow(self, mock_neo4j_client):
        """Test complete product and functionality workflow."""
        from mcp_server.tools.product_tools import ProductTools

        # Setup mock responses
        mock_neo4j_client.query.side_effect = [
            # create_product
            [{"p": {"code": "TEST_PROD", "name": "Test Product"}}],
            # get_functionality
            [{"f": {"code": "TEST_FUNC", "name": "Test Functionality"}}],
            # assign_functionality_to_product
            [{"r": {"created_at": "2024-01-01"}}],
            # get_product_with_functionalities
            [
                {
                    "p": {"code": "TEST_PROD", "name": "Test Product"},
                    "functionalities": [
                        {"code": "TEST_FUNC", "name": "Test Functionality"}
                    ],
                    "incidents": [],
                    "resolutions": [],
                }
            ],
        ]

        # Create ProductTools with mock client
        tools = ProductTools()
        # Manually set the mock product manager
        from graph.neo4j_client import Neo4jClient
        from graph.product_manager import ProductManager

        mock_pm = ProductManager(mock_neo4j_client)
        tools._product_manager = mock_pm

        # Execute workflow
        context = Mock(metadata={})
        result = tools.register_product(
            context, "TEST_PROD", "Test Product", ["TEST_FUNC"]
        )

        # Verify results
        assert result["success"] is True
        assert result["product"]["code"] == "TEST_PROD"
        assert len(result["product"]["functionalities"]) == 1

        # Verify mock calls
        assert mock_neo4j_client.query.call_count == 4
