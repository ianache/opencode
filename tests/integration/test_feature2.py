"""
Integration tests for Feature 2: MCP API.

Tests complete MCP server functionality including
authentication, tools, and resources with end-to-end workflows.
"""

import pytest
import time
from unittest.mock import Mock, patch

# Import MCP server components
try:
    from mcp_server.server import create_mcp_server
    from mcp_server.auth.jwt_handler import JWTHandler
    from mcp_server.tools.product_tools import ProductTools
    from mcp_server.tools.functionality_tools import FunctionalityTools
    from mcp_server.resources.product_resources import ProductResources
except ImportError as e:
    pytest.skip(f"MCP server dependencies not available: {e}")


class TestFeature2Integration:
    """Integration tests for Feature 2 MCP API functionality."""

    @pytest.fixture
    def mock_neo4j_client(self):
        """Create a mock Neo4j client."""
        return Mock(spec=["query"])

    @pytest.fixture
    def jwt_handler(self):
        """Create JWT handler for testing."""
        return JWTHandler("test-secret-key")

    @pytest.fixture
    def mcp_server(self):
        """Create configured MCP server."""
        with patch("mcp_server.config.mcp_config.MCPServerConfig") as mock_config:
            mock_config.return_value = Mock(
                server_name="Test MCP Server",
                host="127.0.0.1",
                port=8000,
                transport="stdio",
                auth_enabled=True,
                jwt_secret_key="test-secret-key",
            )
            return create_mcp_server()

    @pytest.fixture
    def sample_product_data(self):
        """Sample product data for testing."""
        return {
            "product": {
                "code": "TEST_PROD",
                "name": "Test Product System",
                "functionalities": ["REPORTES", "CONTABILIDAD", "GESTION"],
            },
            "functionalities": [
                {"code": "REPORTES", "name": "Report Generation"},
                {"code": "CONTABILIDAD", "name": "Capacity Management"},
                {"code": "GESTION", "name": "Resource Management"},
            ],
        }

    def test_jwt_token_generation_and_validation(self, jwt_handler):
        """Test JWT token generation and validation workflow."""
        # Generate token
        token = jwt_handler.generate_token("testuser", {"role": "admin"})
        assert token is not None
        assert isinstance(token, str)

        # Validate token
        payload = jwt_handler.validate_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_mcp_server_initialization(self, mcp_server):
        """Test MCP server initialization and configuration."""
        # Check that server was created
        assert mcp_server is not None

        # Check server attributes
        assert hasattr(mcp_server, "tools")
        assert hasattr(mcp_server, "resources")
        assert len(mcp_server.tools) > 0
        assert len(mcp_server.resources) > 0

    def test_complete_product_registration_workflow(
        self, mock_neo4j_client, sample_product_data
    ):
        """Test complete workflow: product registration with functionality assignment."""
        # Setup mock responses for Neo4j queries
        mock_neo4j_client.query.side_effect = [
            # create_product
            [
                {
                    "p": {
                        "code": "TEST_PROD",
                        "name": "Test Product System",
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                }
            ],
            # get_functionality (x3)
            [
                {
                    "f": {
                        "code": "REPORTES",
                        "name": "Report Generation",
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                }
            ],
            [
                {
                    "f": {
                        "code": "CONTABILIDAD",
                        "name": "Capacity Management",
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                }
            ],
            [
                {
                    "f": {
                        "code": "GESTION",
                        "name": "Resource Management",
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                }
            ],
            # assign_functionality_to_product (x3)
            [{"r": {"created_at": "2024-01-01T00:00:00Z"}}],
            [{"r": {"created_at": "2024-01-01T00:00:00Z"}}],
            [{"r": {"created_at": "2024-01-01T00:00:00Z"}}],
            # get_product_with_functionalities
            [
                {
                    "p": {"code": "TEST_PROD", "name": "Test Product System"},
                    "functionalities": [
                        {"code": "REPORTES", "name": "Report Generation"},
                        {"code": "CONTABILIDAD", "name": "Capacity Management"},
                        {"code": "GESTION", "name": "Resource Management"},
                    ],
                    "incidents": [],
                    "resolutions": [],
                }
            ],
        ]

        # Create tools with mock client
        with patch(
            "graph.neo4j_client.create_neo4j_client", return_value=mock_neo4j_client
        ):
            with patch("graph.product_manager.ProductManager") as mock_pm_class:
                mock_pm = Mock()
                mock_pm_class.return_value = mock_pm

                # Initialize product tools
                product_tools = ProductTools()
                product_tools._product_manager = mock_pm

                # Mock context
                mock_context = Mock(metadata={"user": {"sub": "testuser"}})

                # Execute product registration
                result = product_tools.register_product(
                    mock_context,
                    "TEST_PROD",
                    "Test Product System",
                    ["REPORTES", "CONTABILIDAD", "GESTION"],
                )

                # Verify successful response
                assert result["success"] is True
                assert result["product"]["code"] == "TEST_PROD"
                assert result["product"]["name"] == "Test Product System"
                assert result["product"]["functionality_count"] == 3
                assert len(result["product"]["functionalities"]) == 3

                # Verify correct methods were called
                assert mock_pm.create_product.call_count == 1
                assert mock_pm.assign_functionality_to_product.call_count == 3

    def test_product_registration_validation_errors(self, mock_neo4j_client):
        """Test product registration validation with missing required fields."""
        with patch(
            "graph.neo4j_client.create_neo4j_client", return_value=mock_neo4j_client
        ):
            with patch("graph.product_manager.ProductManager") as mock_pm_class:
                mock_pm = Mock()
                mock_pm_class.return_value = mock_pm

                product_tools = ProductTools()
                product_tools._product_manager = mock_pm
                mock_context = Mock(metadata={"user": {"sub": "testuser"}})

                # Test missing code
                with pytest.raises(Exception) as exc_info:
                    product_tools.register_product(mock_context, "", "Test Product")
                assert "obligatorio" in str(exc_info.value).lower()
                assert "codigo" in str(exc_info.value).lower()

                # Test missing name
                with pytest.raises(Exception) as exc_info:
                    product_tools.register_product(mock_context, "TEST_PROD", "")
                assert "obligatorio" in str(exc_info.value).lower()
                assert "nombre" in str(exc_info.value).lower()

                # Verify no database calls were made for invalid input
                assert mock_pm.create_product.call_count == 0

    def test_mcp_resources_access_patterns(self, mock_neo4j_client):
        """Test MCP resource access patterns and responses."""
        # Setup mock responses
        mock_neo4j_client.query.side_effect = [
            # list_all_products
            [
                {
                    "code": "ERP",
                    "name": "ERP System",
                    "created_at": "2024-01-01T00:00:00Z",
                },
                {
                    "code": "CRM",
                    "name": "CRM System",
                    "created_at": "2024-01-01T00:00:00Z",
                },
            ],
            # get_product_with_functionalities
            [
                {
                    "p": {"code": "ERP", "name": "ERP System"},
                    "functionalities": [
                        {"code": "REPORTES", "name": "Report Generation"}
                    ],
                    "incidents": [],
                    "resolutions": [],
                }
            ],
        ]

        with patch(
            "graph.neo4j_client.create_neo4j_client", return_value=mock_neo4j_client
        ):
            with patch("graph.product_manager.ProductManager") as mock_pm_class:
                mock_pm = Mock()
                mock_pm_class.return_value = mock_pm

                product_resources = ProductResources()
                product_resources._product_manager = mock_pm
                mock_context = Mock(metadata={"user": {"sub": "testuser"}})

                # Test products resource
                result = product_resources.products_resource(
                    mock_context, limit=10, offset=0
                )

                assert result["uri"] == "products://"
                assert len(result["data"]) == 2
                assert result["metadata"]["total"] == 2
                assert result["metadata"]["limit"] == 10
                assert result["metadata"]["offset"] == 0
                assert "self" in result["links"]

                # Test specific product resource
                result = product_resources.product_resource(mock_context, "ERP")

                assert result["uri"] == "product://ERP"
                assert result["data"]["product"]["code"] == "ERP"
                assert result["data"]["product"]["name"] == "ERP System"
                assert len(result["data"]["functionalities"]) == 1
                assert result["data"]["incident_count"] == 0

    def test_authentication_flow_integration(self, jwt_handler):
        """Test complete authentication flow integration."""
        # Test authentication
        auth_result = jwt_handler.generate_auth_response("admin", "admin123")

        assert auth_result["success"] is True
        assert "token" in auth_result
        assert auth_result["username"] == "admin"
        assert auth_result["expires_in"] == 86400

        # Test token validation in protected context
        valid_token = auth_result["token"]
        payload = jwt_handler.validate_token(valid_token)

        assert payload["username"] == "admin"
        assert payload["type"] == "user"

        # Test token refresh
        refreshed_token = jwt_handler.refresh_token(valid_token)
        new_payload = jwt_handler.validate_token(refreshed_token)

        assert new_payload["username"] == "admin"
        assert new_payload["sub"] == "admin"

    def test_error_handling_and_logging(self, mock_neo4j_client):
        """Test error handling and logging patterns."""
        # Setup mock to raise exception
        mock_neo4j_client.query.side_effect = Exception("Database connection lost")

        with patch(
            "graph.neo4j_client.create_neo4j_client", return_value=mock_neo4j_client
        ):
            with patch("graph.product_manager.ProductManager") as mock_pm_class:
                mock_pm = Mock()
                mock_pm_class.return_value = mock_pm

                product_tools = ProductTools()
                product_tools._product_manager = mock_pm
                mock_context = Mock(metadata={"user": {"sub": "testuser"}})

                # Test error propagation
                with pytest.raises(Exception) as exc_info:
                    product_tools.get_product_details(mock_context, "NONEXISTENT")

                # Verify error is properly propagated
                assert "Database connection lost" in str(exc_info.value)

    def test_performance_with_realistic_data(self, mock_neo4j_client):
        """Test performance with realistic data volumes."""
        import time

        # Setup large dataset mock response
        large_products = [
            {
                "code": f"PROD{i:03d}",
                "name": f"Product {i}",
                "created_at": "2024-01-01T00:00:00Z",
            }
            for i in range(1000)
        ]

        mock_neo4j_client.query.return_value = large_products

        with patch(
            "graph.neo4j_client.create_neo4j_client", return_value=mock_neo4j_client
        ):
            with patch("graph.product_manager.ProductManager") as mock_pm_class:
                mock_pm = Mock()
                mock_pm_class.return_value = mock_pm

                product_tools = ProductTools()
                product_tools._product_manager = mock_pm
                mock_context = Mock(metadata={"user": {"sub": "testuser"}})

                # Measure performance
                start_time = time.time()
                result = product_tools.list_products(mock_context, limit=100, offset=0)
                end_time = time.time()

                # Verify performance expectations
                assert (
                    end_time - start_time
                ) < 1.0  # Should complete in under 1 second
                assert result["success"] is True
                assert len(result["products"]) == 100

    def test_end_to_end_workflow_simulation(self, mock_neo4j_client):
        """Test complete end-to-end workflow simulation."""
        # This test simulates a complete user scenario:
        # 1. Authenticate
        # 2. Register product with functionalities
        # 3. Query product details
        # 4. Update product
        # 5. List all products

        workflow_results = []

        with patch(
            "graph.neo4j_client.create_neo4j_client", return_value=mock_neo4j_client
        ):
            with patch("graph.product_manager.ProductManager") as mock_pm_class:
                mock_pm = Mock()
                mock_pm_class.return_value = mock_pm

                # Mock responses for each step
                mock_neo4j_client.query.side_effect = [
                    # create_product
                    [
                        {
                            "p": {
                                "code": "WORKFLOW_PROD",
                                "name": "Workflow Test",
                                "created_at": "2024-01-01T00:00:00Z",
                            }
                        }
                    ],
                    # get_functionality
                    [
                        {
                            "f": {
                                "code": "WORKFLOW_FUNC",
                                "name": "Workflow Function",
                                "created_at": "2024-01-01T00:00:00Z",
                            }
                        }
                    ],
                    # assign_functionality_to_product
                    [{"r": {"created_at": "2024-01-01T00:00:00Z"}}],
                    # get_product_with_functionalities
                    [
                        {
                            "p": {
                                "code": "WORKFLOW_PROD",
                                "name": "Workflow Test",
                                "updated_at": "2024-01-01T01:00:00Z",
                            },
                            "functionalities": [
                                {"code": "WORKFLOW_FUNC", "name": "Workflow Function"}
                            ],
                            "incidents": [],
                            "resolutions": [],
                        }
                    ],
                    # update_product
                    [
                        {
                            "p": {
                                "code": "WORKFLOW_PROD",
                                "name": "Updated Workflow Test",
                                "updated_at": "2024-01-01T02:00:00Z",
                            }
                        }
                    ],
                    # list_all_products
                    [
                        {"code": "WORKFLOW_PROD", "name": "Updated Workflow Test"},
                        {"code": "OTHER_PROD", "name": "Other Product"},
                    ],
                ]

                product_tools = ProductTools()
                product_tools._product_manager = mock_pm
                mock_context = Mock(metadata={"user": {"sub": "testuser"}})

                try:
                    # Step 1: Register product with functionality
                    result1 = product_tools.register_product(
                        mock_context,
                        "WORKFLOW_PROD",
                        "Workflow Test",
                        ["WORKFLOW_FUNC"],
                    )
                    workflow_results.append(("register_product", result1["success"]))

                    # Step 2: Get product details
                    result2 = product_tools.get_product_details(
                        mock_context, "WORKFLOW_PROD"
                    )
                    workflow_results.append(("get_product_details", result2["success"]))

                    # Step 3: Update product
                    result3 = product_tools.update_product(
                        mock_context, "WORKFLOW_PROD", "Updated Workflow Test"
                    )
                    workflow_results.append(("update_product", result3["success"]))

                    # Step 4: List products
                    result4 = product_tools.list_products(mock_context)
                    workflow_results.append(("list_products", result4["success"]))

                    # Verify all steps succeeded
                    assert all(success for _, success in workflow_results)
                    assert len(workflow_results) == 4

                except Exception as e:
                    pytest.fail(f"End-to-end workflow failed: {e}")

    @pytest.mark.integration
    def test_acceptance_criteria_compliance(self, mock_neo4j_client):
        """Test that all acceptance criteria from feature definition are met."""

        # Criterion 1: Product registration with functionalities
        # "Cuando se requiere registrar producto y funcionalidades asignadas entonces un nuevo producto queda registrado,
        #  las funcionalidades quedan registradas y se han asignado dichas funcionalidades al producto."

        with patch(
            "graph.neo4j_client.create_neo4j_client", return_value=mock_neo4j_client
        ):
            with patch("graph.product_manager.ProductManager") as mock_pm_class:
                mock_pm = Mock()
                mock_pm_class.return_value = mock_pm

                product_tools = ProductTools()
                product_tools._product_manager = mock_pm
                mock_context = Mock(metadata={"user": {"sub": "testuser"}})

                # Mock successful operations
                mock_neo4j_client.query.side_effect = [
                    [
                        {
                            "p": {
                                "code": "CRIT1",
                                "name": "Product 1",
                                "created_at": "2024-01-01T00:00:00Z",
                            }
                        }
                    ],
                    [
                        {
                            "f": {
                                "code": "FUNC1",
                                "name": "Function 1",
                                "created_at": "2024-01-01T00:00:00Z",
                            }
                        }
                    ],
                    [{"r": {"created_at": "2024-01-01T00:00:00Z"}}],
                    [
                        {
                            "p": {"code": "CRIT1", "name": "Product 1"},
                            "functionalities": [
                                {"code": "FUNC1", "name": "Function 1"}
                            ],
                            "incidents": [],
                            "resolutions": [],
                        }
                    ],
                ]

                result = product_tools.register_product(
                    mock_context, "CRIT1", "Product 1", ["FUNC1"]
                )

                assert result["success"] is True
                assert result["product"]["code"] == "CRIT1"
                assert len(result["product"]["functionalities"]) == 1

                # Criterion 2: Product registration without functionalities
                # "Cuando se requiere registrar producto sin funcionalidades asignadas entonces un nuevo producto queda registrado."

                mock_neo4j_client.query.side_effect = [
                    [
                        {
                            "p": {
                                "code": "CRIT2",
                                "name": "Product 2",
                                "created_at": "2024-01-01T00:00:00Z",
                            }
                        }
                    ],
                    [
                        {
                            "p": {"code": "CRIT2", "name": "Product 2"},
                            "functionalities": [],
                            "incidents": [],
                            "resolutions": [],
                        }
                    ],
                ]

                result = product_tools.register_product(
                    mock_context, "CRIT2", "Product 2", []
                )

                assert result["success"] is True
                assert result["product"]["code"] == "CRIT2"
                assert len(result["product"]["functionalities"]) == 0

                # Criterion 3: Error handling for missing required fields
                # "Cuando se requiere registrar producto dado que se omite su codigo o nombre entonces se debe reportar error
                #  'Dato obligatorio X omitido' (donde X representa el atributo o atributos omisos)"

                # Test missing code
                with pytest.raises(Exception) as exc_info:
                    product_tools.register_product(mock_context, "", "Product 3")
                error_msg = str(exc_info.value)
                assert "Dato obligatorio" in error_msg
                assert "codigo" in error_msg

                # Test missing name
                with pytest.raises(Exception) as exc_info:
                    product_tools.register_product(mock_context, "CRIT3", "")
                error_msg = str(exc_info.value)
                assert "Dato obligatorio" in error_msg
                assert "nombre" in error_msg

                # Test both missing
                with pytest.raises(Exception) as exc_info:
                    product_tools.register_product(mock_context, "", "")
                error_msg = str(exc_info.value)
                assert "Dato obligatorio" in error_msg
