"""
Sample data loader for Feature 1: Product Management.

Provides realistic sample data for Products, Functionalities, Components,
Incidents, and Resolutions to demonstrate the GraphRAG product management system.
"""

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from loguru import logger

from graph.product_manager import ProductManager


class SampleDataLoader:
    """Loads sample data for product management demonstration."""

    def __init__(self, product_manager: ProductManager):
        """Initialize with a ProductManager instance."""
        self.pm = product_manager

    def load_all_sample_data(self) -> Dict[str, Any]:
        """Load all sample data and return summary."""
        try:
            logger.info("Starting to load sample data...")

            # Create database constraints
            self.pm.create_constraints()

            # Create products
            products = self._create_products()

            # Create functionalities
            functionalities = self._create_functionalities()

            # Create components
            components = self._create_components()

            # Assign functionalities to products
            self._assign_functionalities_to_products()

            # Assign functionalities to components
            self._assign_functionalities_to_components()

            # Create incidents
            incidents = self._create_incidents()

            # Create resolutions
            resolutions = self._create_resolutions()

            summary = {
                "products": len(products),
                "functionalities": len(functionalities),
                "components": len(components),
                "incidents": len(incidents),
                "resolutions": len(resolutions),
            }

            logger.info(f"Sample data loaded successfully: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error loading sample data: {e}")
            raise

    def _create_products(self) -> List[Dict[str, Any]]:
        """Create sample products."""
        products_data = [
            (
                "ERP",
                "Enterprise Resource Planning - Sistema integral de gestión empresarial",
            ),
            (
                "CRM",
                "Customer Relationship Management - Gestión de relaciones con clientes",
            ),
            (
                "HRM",
                "Human Resource Management - Sistema de gestión de recursos humanos",
            ),
            ("SCM", "Supply Chain Management - Gestión de la cadena de suministro"),
            ("BI", "Business Intelligence - Sistema de inteligencia de negocios"),
        ]

        products = []
        for code, name in products_data:
            product = self.pm.create_product(code, name)
            products.append(product)
            logger.info(f"Created product: {code}")

        return products

    def _create_functionalities(self) -> List[Dict[str, Any]]:
        """Create sample functionalities."""
        functionalities_data = [
            ("GESTION_USUARIOS", "Gestión de usuarios y permisos del sistema"),
            ("REPORTES", "Generación de reportes y análisis de datos"),
            ("INTEGRACION_API", "Integración con APIs externas"),
            ("AUTENTICACION", "Sistema de autenticación y seguridad"),
            ("BACKUP", "Sistema de respaldo y recuperación"),
            ("AUDITORIA", "Sistema de auditoría y trazabilidad"),
            ("NOTIFICACIONES", "Sistema de notificaciones y alertas"),
            ("EXPORTAR_DATOS", "Exportación de datos en múltiples formatos"),
            ("BUSQUEDA_AVANZADA", "Motor de búsqueda avanzado"),
            ("DASHBOARD", "Panel de control y métricas en tiempo real"),
        ]

        functionalities = []
        for code, name in functionalities_data:
            functionality = self.pm.create_functionality(code, name)
            functionalities.append(functionality)
            logger.info(f"Created functionality: {code}")

        return functionalities

    def _create_components(self) -> List[Dict[str, Any]]:
        """Create sample components."""
        components_data = [
            ("FRONTEND_WEB", "Interfaz web principal de la aplicación"),
            ("BACKEND_API", "API REST principal del sistema"),
            ("BASE_DATOS", "Base de datos principal PostgreSQL"),
            ("SERVICIO_AUTH", "Microservicio de autenticación"),
            ("SISTEMA_CACHE", "Sistema de caché Redis"),
            ("PROCESAMIENTO_BATCH", "Sistema de procesamiento por lotes"),
            ("SISTEMA_COLAS", "Sistema de gestión de colas RabbitMQ"),
            ("MONITOREO", "Sistema de monitoreo y alertas"),
            ("INTEGRACIONES", "Módulo de integraciones externas"),
            ("SEGURIDAD", "Módulo de seguridad y cifrado"),
        ]

        components = []
        for code, name in components_data:
            component = self.pm.create_component(code, name)
            components.append(component)
            logger.info(f"Created component: {code}")

        return components

    def _assign_functionalities_to_products(self) -> None:
        """Assign functionalities to products."""
        assignments = [
            (
                "ERP",
                [
                    "GESTION_USUARIOS",
                    "REPORTES",
                    "INTEGRACION_API",
                    "AUTENTICACION",
                    "AUDITORIA",
                    "EXPORTAR_DATOS",
                ],
            ),
            (
                "CRM",
                [
                    "GESTION_USUARIOS",
                    "REPORTES",
                    "NOTIFICACIONES",
                    "BUSQUEDA_AVANZADA",
                    "DASHBOARD",
                ],
            ),
            (
                "HRM",
                [
                    "GESTION_USUARIOS",
                    "REPORTES",
                    "AUTENTICACION",
                    "AUDITORIA",
                    "EXPORTAR_DATOS",
                ],
            ),
            (
                "SCM",
                [
                    "INTEGRACION_API",
                    "REPORTES",
                    "NOTIFICACIONES",
                    "BUSQUEDA_AVANZADA",
                    "MONITOREO",
                ],
            ),
            (
                "BI",
                [
                    "REPORTES",
                    "BUSQUEDA_AVANZADA",
                    "DASHBOARD",
                    "EXPORTAR_DATOS",
                    "INTEGRACION_API",
                ],
            ),
        ]

        for product_code, functionality_codes in assignments:
            for functionality_code in functionality_codes:
                self.pm.assign_functionality_to_product(
                    product_code, functionality_code
                )
                logger.info(f"Assigned {functionality_code} to {product_code}")

    def _assign_functionalities_to_components(self) -> None:
        """Assign functionalities to components."""
        assignments = [
            (
                "FRONTEND_WEB",
                ["AUTENTICACION", "DASHBOARD", "BUSQUEDA_AVANZADA", "NOTIFICACIONES"],
            ),
            (
                "BACKEND_API",
                ["INTEGRACION_API", "GESTION_USUARIOS", "AUDITORIA", "EXPORTAR_DATOS"],
            ),
            ("BASE_DATOS", ["BACKUP", "AUDITORIA", "REPORTES"]),
            ("SERVICIO_AUTH", ["AUTENTICACION", "GESTION_USUARIOS", "SEGURIDAD"]),
            ("SISTEMA_CACHE", ["BUSQUEDA_AVANZADA", "DASHBOARD", "REPORTES"]),
            ("PROCESAMIENTO_BATCH", ["REPORTES", "EXPORTAR_DATOS", "BACKUP"]),
            (
                "SISTEMA_COLAS",
                ["NOTIFICACIONES", "INTEGRACION_API", "PROCESAMIENTO_BATCH"],
            ),
            ("MONITOREO", ["AUDITORIA", "NOTIFICACIONES", "DASHBOARD"]),
            ("INTEGRACIONES", ["INTEGRACION_API", "EXPORTAR_DATOS", "MONITOREO"]),
            ("SEGURIDAD", ["AUTENTICACION", "AUDITORIA", "GESTION_USUARIOS"]),
        ]

        for component_code, functionality_codes in assignments:
            for functionality_code in functionality_codes:
                self.pm.assign_functionality_to_component(
                    component_code, functionality_code
                )
                logger.info(f"Assigned {functionality_code} to {component_code}")

    def _create_incidents(self) -> List[Dict[str, Any]]:
        """Create sample incidents."""
        incidents_data = [
            (
                "INC001",
                "Error de autenticación al iniciar sesión",
                "SLA_HIGH",
                "AUTENTICACION",
            ),
            (
                "INC002",
                "Lentitud en la generación de reportes mensuales",
                "SLA_MEDIUM",
                "REPORTES",
            ),
            (
                "INC003",
                "Fallo en la integración con API externa",
                "SLA_CRITICAL",
                "INTEGRACION_API",
            ),
            (
                "INC004",
                "Pérdida de datos en exportación masiva",
                "SLA_CRITICAL",
                "EXPORTAR_DATOS",
            ),
            (
                "INC005",
                "Usuario no puede acceder al dashboard",
                "SLA_MEDIUM",
                "DASHBOARD",
            ),
            (
                "INC006",
                "Timeout en búsqueda avanzada con grandes volúmenes",
                "SLA_MEDIUM",
                "BUSQUEDA_AVANZADA",
            ),
            (
                "INC007",
                "Notificaciones no llegan a usuarios finales",
                "SLA_HIGH",
                "NOTIFICACIONES",
            ),
            ("INC008", "Error en auditoría de accesos", "SLA_HIGH", "AUDITORIA"),
            ("INC009", "Fallo en backup programado", "SLA_CRITICAL", "BACKUP"),
            (
                "INC010",
                "Problemas de rendimiento en gestión de usuarios",
                "SLA_LOW",
                "GESTION_USUARIOS",
            ),
        ]

        incidents = []
        for code, description, sla_level, functionality_code in incidents_data:
            incident = self.pm.create_incident(
                code, description, sla_level, functionality_code
            )
            incidents.append(incident)
            logger.info(f"Created incident: {code}")

        return incidents

    def _create_resolutions(self) -> List[Dict[str, Any]]:
        """Create sample resolutions."""
        resolutions_data = [
            (
                "INC001",
                "2024-01-15T10:30:00Z",
                "Se reinició el servicio de autenticación y se limpió la caché de sesiones",
            ),
            (
                "INC002",
                "2024-01-16T14:20:00Z",
                "Se optimizaron las consultas SQL y se agregaron índices a la base de datos",
            ),
            (
                "INC003",
                "2024-01-14T09:15:00Z",
                "Se actualizó la versión del cliente HTTP y se reconfiguró el timeout",
            ),
            (
                "INC004",
                "2024-01-13T16:45:00Z",
                "Se implementó procesamiento por lotes y se agregó validación de memoria",
            ),
            (
                "INC005",
                "2024-01-17T11:00:00Z",
                "Se repararon los permisos de acceso y se regeneraron los tokens de sesión",
            ),
            (
                "INC006",
                "2024-01-18T13:30:00Z",
                "Se implementó paginación y se mejoró el algoritmo de indexación",
            ),
            (
                "INC007",
                "2024-01-16T15:45:00Z",
                "Se reconfiguró el servidor de correos y se verificaron las plantillas",
            ),
            (
                "INC008",
                "2024-01-15T12:00:00Z",
                "Se reparó el trigger de auditoría y se reconstruyeron los logs",
            ),
            (
                "INC009",
                "2024-01-13T08:00:00Z",
                "Se incrementó el espacio en disco y se reconfiguró el schedule",
            ),
            (
                "INC010",
                "2024-01-19T17:20:00Z",
                "Se actualizó la librería de ORM y se optimizaron las consultas",
            ),
        ]

        resolutions = []
        for incident_code, resolution_date, procedure in resolutions_data:
            resolution = self.pm.create_resolution(
                incident_code, resolution_date, procedure
            )
            resolutions.append(resolution)
            logger.info(f"Created resolution for incident: {incident_code}")

        return resolutions

    def clear_all_data(self) -> None:
        """Clear all sample data from the database."""
        try:
            logger.info("Clearing all sample data...")

            # Delete in order to respect constraints
            clear_queries = [
                "MATCH (r:Resolution) DELETE r",
                "MATCH (i:Incident) DELETE i",
                "MATCH ()-[r:ASIGNACION_FUNCIONALIDAD]->() DELETE r",
                "MATCH (f:Functionality) DELETE f",
                "MATCH (c:Component) DELETE c",
                "MATCH (p:Product) DELETE p",
            ]

            for query in clear_queries:
                self.pm.client.query(query)

            logger.info("All sample data cleared successfully")

        except Exception as e:
            logger.error(f"Error clearing sample data: {e}")
            raise

    def get_demo_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded sample data."""
        try:
            stats = {
                "products_summary": self.pm.get_all_products_summary(),
                "total_products": len(self.pm.list_all_products()),
            }

            # Get detailed info for first product as example
            products = self.pm.list_all_products()
            if products:
                first_product = self.pm.get_product_with_functionalities(
                    products[0]["code"]
                )
                stats["example_product"] = first_product

            return stats

        except Exception as e:
            logger.error(f"Error getting demo statistics: {e}")
            raise
