"""
Integration tests for Feature 3: Incident Registration functionality.

Tests the complete workflow for registering incidents on functionalities
as specified in the feature requirements.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from mcp_server.models.requests import IncidentRegistrationRequest
from mcp_server.tools.incident_tools import IncidentTools


class TestFeature3IncidentRegistration:
    """Integration tests for Feature 3 incident registration."""

    @patch("mcp_server.tools.incident_tools.create_neo4j_client")
    @patch("mcp_server.tools.incident_tools.ProductManager")
    def test_feature3_complete_incident_registration(
        self, mock_pm_class, mock_create_client
    ):
        """Test complete incident registration workflow as per Feature 3 requirements."""
        # Setup mocks
        mock_client = Mock()
        mock_product_manager = Mock()
        mock_create_client.return_value = mock_client
        mock_pm_class.return_value = mock_product_manager

        # Mock existing functionality
        mock_functionality = {
            "code": "FUNC_BILLING",
            "name": "Billing Functionality",
            "created_at": datetime.now(),
        }
        mock_product_manager.get_functionality.return_value = mock_functionality

        # Mock created incident
        mock_incident = {
            "code": "INC_BILLING_001",
            "description": "Billing system not processing payments",
            "sla_level": "SLA_CRITICAL",
            "created_at": datetime.now(),
        }
        mock_product_manager.create_incident.return_value = mock_incident

        # Initialize incident tools
        incident_tools = IncidentTools()

        # Create incident registration request with all required fields from ontological model
        incident_request = IncidentRegistrationRequest(
            code="INC_BILLING_001",
            description="Billing system not processing payments",
            sla_level="SLA_CRITICAL",  # Highest SLA level as per requirement
            functionality_code="FUNC_BILLING",
        )

        # Mock context
        mock_ctx = Mock()

        # Register incident
        result = incident_tools.register_incident(mock_ctx, incident_request)

        # Verify Feature 3 acceptance criteria:
        # 1. Incident is registered according to ontological model data
        assert result["success"] is True
        assert "INC_BILLING_001" in result["message"]
        assert "registered successfully" in result["message"]

        incident_data = result["incident"]
        assert incident_data["code"] == "INC_BILLING_001"
        assert incident_data["description"] == "Billing system not processing payments"
        assert incident_data["sla_level"] == "SLA_CRITICAL"
        assert incident_data["functionality_code"] == "FUNC_BILLING"

        # 2. Proper reference to functionality relationship
        mock_product_manager.get_functionality.assert_called_once_with("FUNC_BILLING")
        mock_product_manager.create_incident.assert_called_once_with(
            code="INC_BILLING_001",
            description="Billing system not processing payments",
            sla_level="SLA_CRITICAL",
            functionality_code="FUNC_BILLING",
        )

    @patch("mcp_server.tools.incident_tools.create_neo4j_client")
    @patch("mcp_server.tools.incident_tools.ProductManager")
    def test_feature3_incomplete_data_error(self, mock_pm_class, mock_create_client):
        """Test incomplete data error as per Feature 3 criteria."""
        # Setup mocks
        mock_client = Mock()
        mock_product_manager = Mock()
        mock_create_client.return_value = mock_client
        mock_pm_class.return_value = mock_product_manager

        incident_tools = IncidentTools()
        mock_ctx = Mock()

        # Test with incomplete data - missing description (ontological model field)
        with pytest.raises(Exception) as exc_info:
            # This should fail at Pydantic validation level
            IncidentRegistrationRequest(
                code="INC_001",
                description="",  # Missing required field
                sla_level="SLA_HIGH",
                functionality_code="FUNC_001",
            )

        # Should validate that all ontological model attributes are provided
        assert "String should have at least 1 character" in str(exc_info.value)

    @patch("mcp_server.tools.incident_tools.create_neo4j_client")
    @patch("mcp_server.tools.incident_tools.ProductManager")
    def test_feature3_sla_levels_supported(self, mock_pm_class, mock_create_client):
        """Test that all SLA levels from the ontology are supported."""
        mock_client = Mock()
        mock_product_manager = Mock()
        mock_create_client.return_value = mock_client
        mock_pm_class.return_value = mock_product_manager

        # Mock existing functionality
        mock_product_manager.get_functionality.return_value = {
            "code": "FUNC_001",
            "name": "Test Functionality",
            "created_at": datetime.now(),
        }

        def mock_create_incident(*args, **kwargs):
            return {
                "code": kwargs.get("code", "INC_001"),
                "description": kwargs.get("description", "Test incident"),
                "sla_level": kwargs.get("sla_level", "SLA_CRITICAL"),
                "created_at": datetime.now(),
            }

        mock_product_manager.create_incident.side_effect = mock_create_incident

        incident_tools = IncidentTools()
        mock_ctx = Mock()

        # Test all valid SLA levels
        valid_sla_levels = ["SLA_CRITICAL", "SLA_HIGH", "SLA_MEDIUM", "SLA_LOW"]

        for sla_level in valid_sla_levels:
            incident_request = IncidentRegistrationRequest(
                code=f"INC_{sla_level}",
                description=f"Test incident with {sla_level}",
                sla_level=sla_level,
                functionality_code="FUNC_001",
            )

            result = incident_tools.register_incident(mock_ctx, incident_request)
            assert result["success"] is True
            assert result["incident"]["sla_level"] == sla_level

    @patch("mcp_server.tools.incident_tools.create_neo4j_client")
    @patch("mcp_server.tools.incident_tools.ProductManager")
    def test_feature3_invalid_sla_level_rejected(
        self, mock_pm_class, mock_create_client
    ):
        """Test that invalid SLA levels are rejected."""
        mock_client = Mock()
        mock_product_manager = Mock()
        mock_create_client.return_value = mock_client
        mock_pm_class.return_value = mock_product_manager

        incident_tools = IncidentTools()

        # Test invalid SLA level
        with pytest.raises(Exception) as exc_info:
            IncidentRegistrationRequest(
                code="INC_001",
                description="Test incident",
                sla_level="INVALID_SLA",
                functionality_code="FUNC_001",
            )

        assert "SLA level must be one of" in str(exc_info.value)
        assert "SLA_CRITICAL" in str(exc_info.value)
        assert "SLA_HIGH" in str(exc_info.value)
        assert "SLA_MEDIUM" in str(exc_info.value)
        assert "SLA_LOW" in str(exc_info.value)

    @patch("mcp_server.tools.incident_tools.create_neo4j_client")
    @patch("mcp_server.tools.incident_tools.ProductManager")
    def test_feature3_functionality_not_found(self, mock_pm_class, mock_create_client):
        """Test behavior when functionality doesn't exist."""
        mock_client = Mock()
        mock_product_manager = Mock()
        mock_create_client.return_value = mock_client
        mock_pm_class.return_value = mock_product_manager

        # Mock functionality not found
        mock_product_manager.get_functionality.return_value = None

        incident_tools = IncidentTools()

        incident_request = IncidentRegistrationRequest(
            code="INC_001",
            description="Test incident",
            sla_level="SLA_HIGH",
            functionality_code="NONEXISTENT_FUNC",
        )

        mock_ctx = Mock()

        # Should fail when functionality doesn't exist
        with pytest.raises(Exception) as exc_info:
            incident_tools.register_incident(mock_ctx, incident_request)

        assert "Functionality 'NONEXISTENT_FUNC' not found" in str(exc_info.value)

    @patch("mcp_server.tools.incident_tools.create_neo4j_client")
    @patch("mcp_server.tools.incident_tools.ProductManager")
    def test_feature3_duplicate_incident_handling(
        self, mock_pm_class, mock_create_client
    ):
        """Test handling of duplicate incident codes."""
        mock_client = Mock()
        mock_product_manager = Mock()
        mock_create_client.return_value = mock_client
        mock_pm_class.return_value = mock_product_manager

        # Mock existing functionality
        mock_product_manager.get_functionality.return_value = {
            "code": "FUNC_001",
            "name": "Test Functionality",
            "created_at": datetime.now(),
        }

        # Mock database constraint violation for duplicate incident
        mock_product_manager.create_incident.side_effect = Exception(
            "Incident with code 'INC_001' already exists"
        )

        incident_tools = IncidentTools()

        incident_request = IncidentRegistrationRequest(
            code="INC_001",
            description="Test incident",
            sla_level="SLA_HIGH",
            functionality_code="FUNC_001",
        )

        mock_ctx = Mock()

        # Should handle duplicate incident gracefully
        with pytest.raises(Exception) as exc_info:
            incident_tools.register_incident(mock_ctx, incident_request)

        assert "already exists" in str(exc_info.value)
        assert "INC_001" in str(exc_info.value)
