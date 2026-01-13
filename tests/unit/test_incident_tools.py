"""
Unit tests for IncidentTools module.

Tests incident management functionality including registration,
validation, and queries.
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from graph.neo4j_client import Neo4jClient
from graph.product_manager import ProductManager
from mcp_server.tools.incident_tools import IncidentTools
from mcp_server.models.requests import IncidentRegistrationRequest


class TestIncidentTools:
    """Test cases for IncidentTools class."""

    def test_initialization(self):
        """Test IncidentTools initialization."""
        mock_client = Mock(spec=Neo4jClient)
        mock_product_manager = Mock(spec=ProductManager)

        with patch(
            "mcp_server.tools.incident_tools.create_neo4j_client",
            return_value=mock_client,
        ):
            with patch(
                "mcp_server.tools.incident_tools.ProductManager",
                return_value=mock_product_manager,
            ):
                incident_tools = IncidentTools()
                assert incident_tools.product_manager == mock_product_manager
                assert incident_tools.neo4j_client == mock_client

    @patch("mcp_server.tools.incident_tools.logger")
    def test_register_incident_success(self, mock_logger):
        """Test successful incident registration."""
        # Setup mocks
        mock_client = Mock(spec=Neo4jClient)
        mock_product_manager = Mock(spec=ProductManager)

        mock_functionality = {
            "code": "FUNC001",
            "name": "Test Functionality",
            "created_at": datetime.now(),
        }

        mock_incident = {
            "code": "INC001",
            "description": "Test incident description",
            "sla_level": "SLA_HIGH",
            "created_at": datetime.now(),
        }

        mock_product_manager.get_functionality.return_value = mock_functionality
        mock_product_manager.create_incident.return_value = mock_incident

        with patch(
            "mcp_server.tools.incident_tools.create_neo4j_client",
            return_value=mock_client,
        ):
            with patch(
                "mcp_server.tools.incident_tools.ProductManager",
                return_value=mock_product_manager,
            ):
                incident_tools = IncidentTools()

                # Test data
                incident_data = IncidentRegistrationRequest(
                    code="INC001",
                    description="Test incident description",
                    sla_level="SLA_HIGH",
                    functionality_code="FUNC001",
                )

                # Mock context
                mock_ctx = Mock()

                # Test
                result = incident_tools.register_incident(mock_ctx, incident_data)

                # Assertions
                assert result["success"] is True
                assert "INC001" in result["message"]
                assert result["incident"]["code"] == "INC001"
                assert result["incident"]["description"] == "Test incident description"
                assert result["incident"]["sla_level"] == "SLA_HIGH"

                # Verify method calls
                mock_product_manager.get_functionality.assert_called_once_with(
                    "FUNC001"
                )
                mock_product_manager.create_incident.assert_called_once_with(
                    code="INC001",
                    description="Test incident description",
                    sla_level="SLA_HIGH",
                    functionality_code="FUNC001",
                )

    @patch("mcp_server.tools.incident_tools.logger")
    def test_register_incident_incomplete_data(self, mock_logger):
        """Test incident registration with incomplete data."""
        mock_client = Mock(spec=Neo4jClient)
        mock_product_manager = Mock(spec=ProductManager)

        with patch(
            "mcp_server.tools.incident_tools.create_neo4j_client",
            return_value=mock_client,
        ):
            with patch(
                "mcp_server.tools.incident_tools.ProductManager",
                return_value=mock_product_manager,
            ):
                incident_tools = IncidentTools()

                # Test that Pydantic validation catches empty description at object creation
                with pytest.raises(Exception) as exc_info:
                    IncidentRegistrationRequest(
                        code="INC001",
                        description="",  # Empty description should trigger validation
                        sla_level="SLA_HIGH",
                        functionality_code="FUNC001",
                    )

                # Pydantic validation will catch this before our method is called
                assert "String should have at least 1 character" in str(exc_info.value)

    @patch("mcp_server.tools.incident_tools.logger")
    def test_register_incident_functionality_not_found(self, mock_logger):
        """Test incident registration with non-existent functionality."""
        mock_client = Mock(spec=Neo4jClient)
        mock_product_manager = Mock(spec=ProductManager)

        mock_product_manager.get_functionality.return_value = None

        with patch(
            "mcp_server.tools.incident_tools.create_neo4j_client",
            return_value=mock_client,
        ):
            with patch(
                "mcp_server.tools.incident_tools.ProductManager",
                return_value=mock_product_manager,
            ):
                incident_tools = IncidentTools()

                incident_data = IncidentRegistrationRequest(
                    code="INC001",
                    description="Test incident description",
                    sla_level="SLA_HIGH",
                    functionality_code="NONEXISTENT",
                )

                mock_ctx = Mock()

                # Test and assert exception
                with pytest.raises(Exception) as exc_info:
                    incident_tools.register_incident(mock_ctx, incident_data)

                assert "Functionality 'NONEXISTENT' not found" in str(exc_info.value)

    @patch("mcp_server.tools.incident_tools.logger")
    def test_get_incident_details_success(self, mock_logger):
        """Test successful incident details retrieval."""
        mock_client = Mock(spec=Neo4jClient)
        mock_product_manager = Mock(spec=ProductManager)

        mock_incident = {
            "code": "INC001",
            "description": "Test incident description",
            "sla_level": "SLA_HIGH",
            "created_at": datetime.now(),
        }

        mock_product_manager.get_incident.return_value = mock_incident

        with patch(
            "mcp_server.tools.incident_tools.create_neo4j_client",
            return_value=mock_client,
        ):
            with patch(
                "mcp_server.tools.incident_tools.ProductManager",
                return_value=mock_product_manager,
            ):
                incident_tools = IncidentTools()

                mock_ctx = Mock()

                # Test
                result = incident_tools.get_incident_details(mock_ctx, "INC001")

                # Assertions
                assert result["success"] is True
                assert result["incident"]["code"] == "INC001"
                assert result["incident"]["description"] == "Test incident description"
                assert result["incident"]["sla_level"] == "SLA_HIGH"

                mock_product_manager.get_incident.assert_called_once_with("INC001")

    @patch("mcp_server.tools.incident_tools.logger")
    def test_get_incident_details_not_found(self, mock_logger):
        """Test incident details retrieval for non-existent incident."""
        mock_client = Mock(spec=Neo4jClient)
        mock_product_manager = Mock(spec=ProductManager)

        mock_product_manager.get_incident.return_value = None

        with patch(
            "mcp_server.tools.incident_tools.create_neo4j_client",
            return_value=mock_client,
        ):
            with patch(
                "mcp_server.tools.incident_tools.ProductManager",
                return_value=mock_product_manager,
            ):
                incident_tools = IncidentTools()

                mock_ctx = Mock()

                # Test and assert exception
                with pytest.raises(Exception) as exc_info:
                    incident_tools.get_incident_details(mock_ctx, "NONEXISTENT")

                assert "Incident 'NONEXISTENT' not found" in str(exc_info.value)

    @patch("mcp_server.tools.incident_tools.logger")
    def test_list_incidents_by_functionality_success(self, mock_logger):
        """Test successful listing incidents by functionality."""
        mock_client = Mock(spec=Neo4jClient)
        mock_product_manager = Mock(spec=ProductManager)

        mock_functionality = {
            "code": "FUNC001",
            "name": "Test Functionality",
            "created_at": datetime.now(),
        }

        mock_incidents = [
            {
                "i": {
                    "code": "INC001",
                    "description": "Incident 1",
                    "sla_level": "SLA_HIGH",
                    "created_at": datetime.now(),
                }
            },
            {
                "i": {
                    "code": "INC002",
                    "description": "Incident 2",
                    "sla_level": "SLA_MEDIUM",
                    "created_at": datetime.now(),
                }
            },
        ]

        mock_product_manager.get_functionality.return_value = mock_functionality
        mock_product_manager.get_incidents_by_functionality.return_value = (
            mock_incidents
        )

        with patch(
            "mcp_server.tools.incident_tools.create_neo4j_client",
            return_value=mock_client,
        ):
            with patch(
                "mcp_server.tools.incident_tools.ProductManager",
                return_value=mock_product_manager,
            ):
                incident_tools = IncidentTools()

                mock_ctx = Mock()

                # Test
                result = incident_tools.list_incidents_by_functionality(
                    mock_ctx, "FUNC001", 50, 0
                )

                # Assertions
                assert result["success"] is True
                assert result["functionality_code"] == "FUNC001"
                assert result["total"] == 2
                assert len(result["incidents"]) == 2

                mock_product_manager.get_functionality.assert_called_once_with(
                    "FUNC001"
                )
                mock_product_manager.get_incidents_by_functionality.assert_called_once_with(
                    "FUNC001"
                )

    @patch("mcp_server.tools.incident_tools.logger")
    def test_list_incidents_by_functionality_not_found(self, mock_logger):
        """Test listing incidents for non-existent functionality."""
        mock_client = Mock(spec=Neo4jClient)
        mock_product_manager = Mock(spec=ProductManager)

        mock_product_manager.get_functionality.return_value = None

        with patch(
            "mcp_server.tools.incident_tools.create_neo4j_client",
            return_value=mock_client,
        ):
            with patch(
                "mcp_server.tools.incident_tools.ProductManager",
                return_value=mock_product_manager,
            ):
                incident_tools = IncidentTools()

                mock_ctx = Mock()

                # Test and assert exception
                with pytest.raises(Exception) as exc_info:
                    incident_tools.list_incidents_by_functionality(
                        mock_ctx, "NONEXISTENT"
                    )

                assert "Functionality 'NONEXISTENT' not found" in str(exc_info.value)

    def test_serialize_datetime_with_datetime(self):
        """Test serialize_datetime function with Python datetime."""
        from mcp_server.tools.incident_tools import serialize_datetime

        test_datetime = datetime(2023, 1, 1, 12, 0, 0)
        result = serialize_datetime(test_datetime)

        assert result == "2023-01-01T12:00:00"

    def test_serialize_datetime_with_none(self):
        """Test serialize_datetime function with None."""
        from mcp_server.tools.incident_tools import serialize_datetime

        result = serialize_datetime(None)
        assert result is None

    def test_serialize_datetime_with_dict(self):
        """Test serialize_datetime function with dictionary containing datetime."""
        from mcp_server.tools.incident_tools import serialize_datetime

        test_dict = {
            "code": "INC001",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "description": "Test",
        }

        result = serialize_datetime(test_dict)

        assert result["code"] == "INC001"
        assert result["description"] == "Test"
        assert result["created_at"] == "2023-01-01T12:00:00"

    def test_serialize_datetime_with_list(self):
        """Test serialize_datetime function with list containing datetime."""
        from mcp_server.tools.incident_tools import serialize_datetime

        test_list = [
            {"code": "INC001", "created_at": datetime(2023, 1, 1, 12, 0, 0)},
            {"code": "INC002", "created_at": datetime(2023, 1, 2, 12, 0, 0)},
        ]

        result = serialize_datetime(test_list)

        assert len(result) == 2
        assert result[0]["created_at"] == "2023-01-01T12:00:00"
        assert result[1]["created_at"] == "2023-01-02T12:00:00"


class TestIncidentRegistrationRequest:
    """Test cases for IncidentRegistrationRequest validation."""

    def test_valid_incident_request(self):
        """Test valid incident registration request."""
        request = IncidentRegistrationRequest(
            code="INC001",
            description="Test incident description",
            sla_level="SLA_HIGH",
            functionality_code="FUNC001",
        )

        assert request.code == "INC001"
        assert request.description == "Test incident description"
        assert request.sla_level == "SLA_HIGH"
        assert request.functionality_code == "FUNC001"

    def test_invalid_sla_level(self):
        """Test validation of invalid SLA level."""
        with pytest.raises(Exception) as exc_info:
            IncidentRegistrationRequest(
                code="INC001",
                description="Test incident description",
                sla_level="INVALID_SLA",
                functionality_code="FUNC001",
            )

        assert "SLA level must be one of" in str(exc_info.value)

    def test_empty_code_validation(self):
        """Test validation of empty code."""
        with pytest.raises(Exception) as exc_info:
            IncidentRegistrationRequest(
                code="",
                description="Test incident description",
                sla_level="SLA_HIGH",
                functionality_code="FUNC001",
            )
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_empty_description_validation(self):
        """Test validation of empty description."""
        with pytest.raises(Exception) as exc_info:
            IncidentRegistrationRequest(
                code="INC001",
                description="",
                sla_level="SLA_HIGH",
                functionality_code="FUNC001",
            )
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_empty_functionality_code_validation(self):
        """Test validation of empty functionality code."""
        with pytest.raises(Exception) as exc_info:
            IncidentRegistrationRequest(
                code="INC001",
                description="Test incident description",
                sla_level="SLA_HIGH",
                functionality_code="",
            )
        assert "String should have at least 1 character" in str(exc_info.value)
