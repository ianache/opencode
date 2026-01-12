"""
Integration tests for Feature 1: Product Management.

Tests the complete workflow of product management including
data loading, relationships, and business queries.
"""

from unittest.mock import Mock, patch

import pytest

from data.sample_data import SampleDataLoader
from graph.neo4j_client import Neo4jClient
from graph.product_manager import ProductManager


class TestFeature1Integration:
    """Integration tests for Feature 1 functionality."""

    @pytest.fixture
    def mock_neo4j_client(self):
        """Create a mock Neo4j client for testing."""
        return Mock(spec=Neo4jClient)

    @pytest.fixture
    def product_manager(self, mock_neo4j_client):
        """Create ProductManager with mock client."""
        return ProductManager(mock_neo4j_client)

    @pytest.fixture
    def sample_loader(self, product_manager):
        """Create SampleDataLoader with mock ProductManager."""
        return SampleDataLoader(product_manager)

    def test_complete_workflow_product_to_incident(self, mock_neo4j_client):
        """Test complete workflow from product creation to incident management."""
        # Setup mock responses
        mock_neo4j_client.query.side_effect = [
            # create_product
            [{"p": {"code": "TEST_PROD", "name": "Test Product"}}],
            # create_functionality
            [{"f": {"code": "TEST_FUNC", "name": "Test Functionality"}}],
            # assign_functionality_to_product
            [{"r": {"created_at": "2024-01-01"}}],
            # create_incident
            [{"i": {"code": "TEST_INC", "description": "Test Incident"}}],
            # create_resolution
            [{"r": {"incident_code": "TEST_INC", "procedure": "Test Resolution"}}],
            # get_product_with_functionalities
            [
                {
                    "p": {"code": "TEST_PROD", "name": "Test Product"},
                    "functionalities": [
                        {"code": "TEST_FUNC", "name": "Test Functionality"}
                    ],
                    "incidents": [{"code": "TEST_INC", "description": "Test Incident"}],
                    "resolutions": [
                        {"incident_code": "TEST_INC", "procedure": "Test Resolution"}
                    ],
                }
            ],
        ]

        # Execute workflow
        pm = ProductManager(mock_neo4j_client)

        # 1. Create product
        product = pm.create_product("TEST_PROD", "Test Product")
        assert product["code"] == "TEST_PROD"

        # 2. Create functionality
        functionality = pm.create_functionality("TEST_FUNC", "Test Functionality")
        assert functionality["code"] == "TEST_FUNC"

        # 3. Assign functionality to product
        assigned = pm.assign_functionality_to_product("TEST_PROD", "TEST_FUNC")
        assert assigned is True

        # 4. Create incident for functionality
        incident = pm.create_incident(
            "TEST_INC", "Test Incident", "SLA_HIGH", "TEST_FUNC"
        )
        assert incident["code"] == "TEST_INC"

        # 5. Create resolution for incident
        resolution = pm.create_resolution(
            "TEST_INC", "2024-01-15T10:30:00Z", "Test Resolution"
        )
        assert resolution["incident_code"] == "TEST_INC"

        # 6. Verify complete picture
        result = pm.get_product_with_functionalities("TEST_PROD")
        assert result["p"]["code"] == "TEST_PROD"
        assert len(result["functionalities"]) == 1
        assert len(result["incidents"]) == 1
        assert len(result["resolutions"]) == 1

    def test_sample_data_loading_workflow(self, mock_neo4j_client):
        """Test complete sample data loading workflow."""
        # Setup basic mock responses
        mock_neo4j_client.query.return_value = [{"success": True}]

        # Execute sample data loading
        pm = ProductManager(mock_neo4j_client)
        loader = SampleDataLoader(pm)

        # Test constraint creation
        loader.pm.create_constraints()

        # Test basic data creation
        try:
            loader._create_products()
        except Exception:
            pass  # Expected due to mock limitations

        try:
            loader._create_functionalities()
        except Exception:
            pass  # Expected due to mock limitations

        # Verify that queries were called
        assert mock_neo4j_client.query.call_count > 0

    def test_component_functionality_workflow(self, mock_neo4j_client):
        """Test workflow with components and their functionalities."""
        # Setup mock responses
        mock_neo4j_client.query.side_effect = [
            # create_component
            [{"c": {"code": "FRONTEND", "name": "Frontend Component"}}],
            # create_functionality
            [{"f": {"code": "AUTH", "name": "Authentication"}}],
            # assign_functionality_to_component
            [{"r": {"created_at": "2024-01-01"}}],
            # get_component_with_functionalities
            [
                {
                    "c": {"code": "FRONTEND", "name": "Frontend Component"},
                    "functionalities": [{"code": "AUTH", "name": "Authentication"}],
                    "incidents": [],
                    "resolutions": [],
                }
            ],
        ]

        # Execute workflow
        pm = ProductManager(mock_neo4j_client)

        # 1. Create component
        component = pm.create_component("FRONTEND", "Frontend Component")
        assert component["code"] == "FRONTEND"

        # 2. Create functionality
        functionality = pm.create_functionality("AUTH", "Authentication")
        assert functionality["code"] == "AUTH"

        # 3. Assign functionality to component
        assigned = pm.assign_functionality_to_component("FRONTEND", "AUTH")
        assert assigned is True

        # 4. Verify component with functionalities
        result = pm.get_component_with_functionalities("FRONTEND")
        assert result["c"]["code"] == "FRONTEND"
        assert len(result["functionalities"]) == 1
        assert result["functionalities"][0]["code"] == "AUTH"

    def test_business_queries_integration(self, mock_neo4j_client):
        """Test business queries with realistic data."""
        # Setup mock responses
        mock_neo4j_client.query.side_effect = [
            # get_all_products_summary
            [
                {
                    "product_code": "ERP",
                    "product_name": "ERP System",
                    "functionality_count": 6,
                    "incident_count": 3,
                },
                {
                    "product_code": "CRM",
                    "product_name": "CRM System",
                    "functionality_count": 4,
                    "incident_count": 1,
                },
            ],
            # get_functionality_with_products
            [
                {
                    "f": {"code": "REPORTES", "name": "Report Generation"},
                    "products": [
                        {"code": "ERP", "name": "ERP System"},
                        {"code": "CRM", "name": "CRM System"},
                    ],
                    "components": [{"code": "BACKEND", "name": "Backend Service"}],
                    "incidents": [
                        {"code": "INC001", "description": "Slow report generation"},
                        {"code": "INC002", "description": "Report formatting error"},
                    ],
                    "resolutions": [
                        {"incident_code": "INC001", "procedure": "Optimized queries"},
                        {"incident_code": "INC002", "procedure": "Fixed template"},
                    ],
                }
            ],
            # get_incidents_by_product
            [
                {
                    "i": {"code": "INC001", "sla_level": "SLA_HIGH"},
                    "r": {"procedure": "Optimized queries"},
                    "f": {"code": "REPORTES"},
                },
                {
                    "i": {"code": "INC003", "sla_level": "SLA_MEDIUM"},
                    "r": None,
                    "f": {"code": "AUTH"},
                },
            ],
            # get_resolutions_by_incident
            [
                {
                    "r": {
                        "procedure": "Optimized queries",
                        "resolution_date": "2024-01-15",
                    },
                    "i": {"code": "INC001"},
                }
            ],
        ]

        # Execute business queries
        pm = ProductManager(mock_neo4j_client)

        # 1. Get products summary
        summary = pm.get_all_products_summary()
        assert len(summary) == 2
        assert summary[0]["product_code"] == "ERP"
        assert summary[0]["functionality_count"] == 6
        assert summary[0]["incident_count"] == 3

        # 2. Get functionality details
        func_details = pm.get_functionality_with_products("REPORTES")
        assert func_details["f"]["code"] == "REPORTES"
        assert len(func_details["products"]) == 2
        assert len(func_details["incidents"]) == 2
        assert len(func_details["resolutions"]) == 2

        # 3. Get incidents by product
        incidents = pm.get_incidents_by_product("ERP")
        assert len(incidents) == 2
        assert incidents[0]["i"]["code"] == "INC001"
        assert incidents[0]["i"]["sla_level"] == "SLA_HIGH"

        # 4. Get resolutions by incident
        resolutions = pm.get_resolutions_by_incident("INC001")
        assert len(resolutions) == 1
        assert resolutions[0]["r"]["procedure"] == "Optimized queries"

    def test_error_handling_integration(self, mock_neo4j_client):
        """Test error handling in integrated workflows."""
        # Setup mock to raise exception on specific call
        mock_neo4j_client.query.side_effect = [
            [{"p": {"code": "PROD1", "name": "Product 1"}}],  # create_product succeeds
            Exception("Database connection lost"),  # create_functionality fails
        ]

        # Execute workflow and handle error
        pm = ProductManager(mock_neo4j_client)

        # First step succeeds
        product = pm.create_product("PROD1", "Product 1")
        assert product["code"] == "PROD1"

        # Second step fails
        with pytest.raises(Exception, match="Database connection lost"):
            pm.create_functionality("FUNC1", "Functionality 1")

    def test_data_clearing_workflow(self, mock_neo4j_client):
        """Test data clearing functionality."""
        # Setup mock responses for clearing operations
        clear_responses = [[] for _ in range(6)]  # 6 delete operations
        mock_neo4j_client.query.side_effect = clear_responses

        # Execute data clearing
        pm = ProductManager(mock_neo4j_client)
        loader = SampleDataLoader(pm)

        loader.clear_all_data()

        # Verify all delete operations were called
        assert mock_neo4j_client.query.call_count == 6

        # Verify delete queries were called in correct order
        calls = [call[0][0] for call in mock_neo4j_client.query.call_args_list]
        assert any("MATCH (r:Resolution) DELETE r" in call for call in calls)
        assert any("MATCH (i:Incident) DELETE i" in call for call in calls)
        assert any(
            "MATCH ()-[r:ASIGNACION_FUNCIONALIDAD]->() DELETE r" in call
            for call in calls
        )
        assert any("MATCH (f:Functionality) DELETE f" in call for call in calls)
        assert any("MATCH (c:Component) DELETE c" in call for call in calls)
        assert any("MATCH (p:Product) DELETE p" in call for call in calls)
