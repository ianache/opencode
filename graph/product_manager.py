"""
Product Manager for GraphRAG application.

Handles product definition and management in Neo4j database,
including Products, Functionalities, Components, Incidents, and Resolutions.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from graph.neo4j_client import Neo4jClient


class ProductManager:
    """Manager for product-related operations in Neo4j."""

    def __init__(self, neo4j_client: Neo4jClient):
        """Initialize ProductManager with Neo4j client."""
        self.client = neo4j_client

    # ==================== PRODUCT METHODS ====================

    def create_product(self, code: str, name: str) -> Dict[str, Any]:
        """Create a new Product node."""
        try:
            query = """
            MERGE (p:Product {code: $code})
            SET p.name = $name, p.created_at = datetime()
            RETURN p
            """
            result = self.client.query(query, {"code": code, "name": name})
            if result:
                logger.info(f"Product created: {code}")
                return result[0]["p"]  # type: ignore
            raise Exception("Failed to create product")
        except Exception as e:
            logger.error(f"Error creating product {code}: {e}")
            raise

    def get_product(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a product by its code."""
        try:
            query = """
            MATCH (p:Product {code: $code})
            RETURN p
            """
            result = self.client.query(query, {"code": code})
            return result[0]["p"] if result else None
        except Exception as e:
            logger.error(f"Error getting product {code}: {e}")
            raise

    def update_product(self, code: str, **kwargs: Any) -> bool:
        """Update product properties."""
        try:
            if not kwargs:
                return False

            set_clause = ", ".join([f"p.{k} = ${k}" for k in kwargs.keys()])
            query = f"""
            MATCH (p:Product {{code: $code}})
            SET {set_clause}, p.updated_at = datetime()
            RETURN p
            """
            params = {"code": code, **kwargs}
            result = self.client.query(query, params)
            if result:
                logger.info(f"Product updated: {code}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating product {code}: {e}")
            raise

    def delete_product(self, code: str) -> bool:
        """Delete a product and its relationships."""
        try:
            query = """
            MATCH (p:Product {code: $code})
            DETACH DELETE p
            RETURN count(p) as deleted
            """
            result = self.client.query(query, {"code": code})
            if result and result[0]["deleted"] > 0:
                logger.info(f"Product deleted: {code}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting product {code}: {e}")
            raise

    def list_all_products(self) -> List[Dict[str, Any]]:
        """List all products."""
        try:
            query = """
            MATCH (p:Product)
            RETURN p
            ORDER BY p.code
            """
            result = self.client.query(query)
            return [item["p"] for item in result]
        except Exception as e:
            logger.error(f"Error listing products: {e}")
            raise

    def search_products(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search products by code or name with fuzzy matching."""
        try:
            # Use a simple fuzzy search on code and name
            query_cypher = """
            MATCH (p:Product)
            WHERE toLower(p.code) CONTAINS toLower($query) 
               OR toLower(p.name) CONTAINS toLower($query)
            RETURN p
            ORDER BY p.code
            LIMIT $limit
            """
            result = self.client.query(query_cypher, {"query": query, "limit": limit})
            return [item["p"] for item in result]
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            raise

    # ==================== FUNCTIONALITY METHODS ====================

    def create_functionality(self, code: str, name: str) -> Dict[str, Any]:
        """Create a new Functionality node."""
        try:
            query = """
            MERGE (f:Functionality {code: $code})
            SET f.name = $name, f.created_at = datetime()
            RETURN f
            """
            result = self.client.query(query, {"code": code, "name": name})
            if result:
                logger.info(f"Functionality created: {code}")
                return result[0]["f"]  # type: ignore
            raise Exception("Failed to create functionality")
        except Exception as e:
            logger.error(f"Error creating functionality {code}: {e}")
            raise

    def get_functionality(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a functionality by its code."""
        try:
            query = """
            MATCH (f:Functionality {code: $code})
            RETURN f
            """
            result = self.client.query(query, {"code": code})
            return result[0]["f"] if result else None
        except Exception as e:
            logger.error(f"Error getting functionality {code}: {e}")
            raise

    # ==================== COMPONENT METHODS ====================

    def create_component(self, code: str, name: str) -> Dict[str, Any]:
        """Create a new Component node."""
        try:
            query = """
            MERGE (c:Component {code: $code})
            SET c.name = $name, c.created_at = datetime()
            RETURN c
            """
            result = self.client.query(query, {"code": code, "name": name})
            if result:
                logger.info(f"Component created: {code}")
                return result[0]["c"]  # type: ignore
            raise Exception("Failed to create component")
        except Exception as e:
            logger.error(f"Error creating component {code}: {e}")
            raise

    def get_component(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a component by its code."""
        try:
            query = """
            MATCH (c:Component {code: $code})
            RETURN c
            """
            result = self.client.query(query, {"code": code})
            return result[0]["c"] if result else None
        except Exception as e:
            logger.error(f"Error getting component {code}: {e}")
            raise

    # ==================== INCIDENT METHODS ====================

    def create_incident(
        self, code: str, description: str, sla_level: str, functionality_code: str
    ) -> Dict[str, Any]:
        """Create a new Incident node linked to functionality."""
        try:
            query = """
            MATCH (f:Functionality {code: $functionality_code})
            MERGE (i:Incident {code: $code})
            SET i.description = $description,
                i.sla_level = $sla_level,
                i.created_at = datetime()
            MERGE (f)-[:HAS_INCIDENT]->(i)
            RETURN i
            """
            params = {
                "code": code,
                "description": description,
                "sla_level": sla_level,
                "functionality_code": functionality_code,
            }
            result = self.client.query(query, params)
            if result:
                logger.info(f"Incident created: {code}")
                return result[0]["i"]  # type: ignore
            raise Exception("Failed to create incident - functionality not found")
        except Exception as e:
            logger.error(f"Error creating incident {code}: {e}")
            raise

    def get_incident(self, code: str) -> Optional[Dict[str, Any]]:
        """Get an incident by its code."""
        try:
            query = """
            MATCH (i:Incident {code: $code})
            RETURN i
            """
            result = self.client.query(query, {"code": code})
            return result[0]["i"] if result else None
        except Exception as e:
            logger.error(f"Error getting incident {code}: {e}")
            raise

    # ==================== RESOLUTION METHODS ====================

    def create_resolution(
        self, incident_code: str, resolution_date: str, procedure: str
    ) -> Dict[str, Any]:
        """Create a new Resolution node linked to incident."""
        try:
            # Parse the resolution_date string to datetime
            try:
                res_date = datetime.fromisoformat(
                    resolution_date.replace("Z", "+00:00")
                )
            except ValueError:
                # If parsing fails, use current date
                res_date = datetime.now()

            query = """
            MATCH (i:Incident {code: $incident_code})
            MERGE (r:Resolution {incident_code: $incident_code})
            SET r.resolution_date = $resolution_date,
                r.procedure = $procedure,
                r.created_at = datetime()
            MERGE (i)-[:HAS_RESOLUTION]->(r)
            RETURN r
            """
            params = {
                "incident_code": incident_code,
                "resolution_date": res_date.isoformat(),
                "procedure": procedure,
            }
            result = self.client.query(query, params)
            if result:
                logger.info(f"Resolution created for incident: {incident_code}")
                return result[0]["r"]  # type: ignore
            raise Exception("Failed to create resolution - incident not found")
        except Exception as e:
            logger.error(f"Error creating resolution for incident {incident_code}: {e}")
            raise

    def get_resolution(self, incident_code: str) -> Optional[Dict[str, Any]]:
        """Get a resolution by incident code."""
        try:
            query = """
            MATCH (r:Resolution {incident_code: $incident_code})
            RETURN r
            """
            result = self.client.query(query, {"incident_code": incident_code})
            return result[0]["r"] if result else None
        except Exception as e:
            logger.error(f"Error getting resolution for incident {incident_code}: {e}")
            raise

    # ==================== RELATIONSHIP METHODS ====================

    def assign_functionality_to_product(
        self, product_code: str, functionality_code: str
    ) -> bool:
        """Create ASIGNACION_FUNCIONALIDAD relationship between Product and Functionality."""
        try:
            query = """
            MATCH (p:Product {code: $product_code})
            MATCH (f:Functionality {code: $functionality_code})
            MERGE (p)-[r:ASIGNACION_FUNCIONALIDAD]->(f)
            SET r.created_at = datetime()
            RETURN r
            """
            params = {
                "product_code": product_code,
                "functionality_code": functionality_code,
            }
            result = self.client.query(query, params)
            if result:
                logger.info(
                    f"Functionality {functionality_code} assigned to product {product_code}"
                )
                return True
            return False
        except Exception as e:
            logger.error(
                f"Error assigning functionality {functionality_code} to product {product_code}: {e}"
            )
            raise

    def assign_functionality_to_component(
        self, component_code: str, functionality_code: str
    ) -> bool:
        """Create ASIGNACION_FUNCIONALIDAD relationship between Component and Functionality."""
        try:
            query = """
            MATCH (c:Component {code: $component_code})
            MATCH (f:Functionality {code: $functionality_code})
            MERGE (c)-[r:ASIGNACION_FUNCIONALIDAD]->(f)
            SET r.created_at = datetime()
            RETURN r
            """
            params = {
                "component_code": component_code,
                "functionality_code": functionality_code,
            }
            result = self.client.query(query, params)
            if result:
                logger.info(
                    f"Functionality {functionality_code} assigned to component {component_code}"
                )
                return True
            return False
        except Exception as e:
            logger.error(
                f"Error assigning functionality {functionality_code} to component {component_code}: {e}"
            )
            raise

    def remove_functionality_from_product(
        self, product_code: str, functionality_code: str
    ) -> bool:
        """Remove ASIGNACION_FUNCIONALIDAD relationship between Product and Functionality."""
        try:
            query = """
            MATCH (p:Product {code: $product_code})-[r:ASIGNACION_FUNCIONALIDAD]->(f:Functionality {code: $functionality_code})
            DELETE r
            RETURN count(r) as deleted
            """
            params = {
                "product_code": product_code,
                "functionality_code": functionality_code,
            }
            result = self.client.query(query, params)
            if result and result[0]["deleted"] > 0:
                logger.info(
                    f"Functionality {functionality_code} removed from product {product_code}"
                )
                return True
            return False
        except Exception as e:
            logger.error(
                f"Error removing functionality {functionality_code} from product {product_code}: {e}"
            )
            raise

    def remove_functionality_from_component(
        self, component_code: str, functionality_code: str
    ) -> bool:
        """Remove ASIGNACION_FUNCIONALIDAD relationship between Component and Functionality."""
        try:
            query = """
            MATCH (c:Component {code: $component_code})-[r:ASIGNACION_FUNCIONALIDAD]->(f:Functionality {code: $functionality_code})
            DELETE r
            RETURN count(r) as deleted
            """
            params = {
                "component_code": component_code,
                "functionality_code": functionality_code,
            }
            result = self.client.query(query, params)
            if result and result[0]["deleted"] > 0:
                logger.info(
                    f"Functionality {functionality_code} removed from component {component_code}"
                )
                return True
            return False
        except Exception as e:
            logger.error(
                f"Error removing functionality {functionality_code} from component {component_code}: {e}"
            )
            raise

    # ==================== BUSINESS QUERY METHODS ====================

    def get_product_with_functionalities(self, product_code: str) -> Dict[str, Any]:
        """Get product with all its assigned functionalities."""
        try:
            query = """
            MATCH (p:Product {code: $product_code})
            OPTIONAL MATCH (p)-[:ASIGNACION_FUNCIONALIDAD]->(f:Functionality)
            OPTIONAL MATCH (f)-[:HAS_INCIDENT]->(i:Incident)
            OPTIONAL MATCH (i)-[:HAS_RESOLUTION]->(r:Resolution)
            RETURN p,
                   collect(DISTINCT f) as functionalities,
                   collect(DISTINCT i) as incidents,
                   collect(DISTINCT r) as resolutions
            """
            result = self.client.query(query, params={"product_code": product_code})
            if result:
                return result[0]
            return {}
        except Exception as e:
            logger.error(
                f"Error getting product {product_code} with functionalities: {e}"
            )
            raise

    def get_functionality_with_products(
        self, functionality_code: str
    ) -> Dict[str, Any]:
        """Get functionality with all associated products and components."""
        try:
            query = """
            MATCH (f:Functionality {code: $functionality_code})
            OPTIONAL MATCH (p:Product)-[:ASIGNACION_FUNCIONALIDAD]->(f)
            OPTIONAL MATCH (f)-[:HAS_COMPONENT]->(c:Component)
            OPTIONAL MATCH (f)-[:HAS_INCIDENT]->(i:Incident)
            OPTIONAL MATCH (i)-[:HAS_RESOLUTION]->(r:Resolution)
            RETURN f,
                   collect(DISTINCT p) as products,
                   collect(DISTINCT c) as components,
                   collect(DISTINCT i) as incidents,
                   collect(DISTINCT r) as resolutions
            """
            result = self.client.query(
                query, {"functionality_code": functionality_code}
            )
            if result:
                return result[0]
            return {}
        except Exception as e:
            logger.error(
                f"Error getting functionality {functionality_code} with products: {e}"
            )
            raise

    def list_functionalities(self) -> List[Dict[str, Any]]:
        """List all functionalities."""
        try:
            query = """
            MATCH (f:Functionality)
            RETURN f
            ORDER BY f.code
            """
            result = self.client.query(query)
            return [item["f"] for item in result]
        except Exception as e:
            logger.error(f"Error listing functionalities: {e}")
            raise

    def get_all_products_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all products with their functionalities."""
        try:
            query = """
            MATCH (p:Product)
            OPTIONAL MATCH (p)-[:ASIGNACION_FUNCIONALIDAD]->(f:Functionality)
            RETURN p, collect(DISTINCT f) as functionalities
            """
            result = self.client.query(query)

            products_summary = []
            for item in result:
                product = item["p"]
                product["functionalities"] = item["functionalities"]
                products_summary.append(product)

            return products_summary
        except Exception as e:
            logger.error(f"Error getting products summary: {e}")
            raise

    def get_component_with_functionalities(self, component_code: str) -> Dict[str, Any]:
        """Get component with all its assigned functionalities."""
        try:
            query = """
            MATCH (c:Component {code: $component_code})
            OPTIONAL MATCH (c)-[:ASIGNACION_FUNCIONALIDAD]->(f:Functionality)
            OPTIONAL MATCH (f)-[:HAS_INCIDENT]->(i:Incident)
            OPTIONAL MATCH (i)-[:HAS_RESOLUTION]->(r:Resolution)
            RETURN c,
                   collect(DISTINCT f) as functionalities,
                   collect(DISTINCT i) as incidents,
                   collect(DISTINCT r) as resolutions
            """
            result = self.client.query(query, {"component_code": component_code})
            if result:
                return result[0]
            return {}
        except Exception as e:
            logger.error(
                f"Error getting component {component_code} with functionalities: {e}"
            )
            raise

    def get_incidents_by_functionality(
        self, functionality_code: str
    ) -> List[Dict[str, Any]]:
        """Get all incidents for a specific functionality."""
        try:
            query = """
            MATCH (f:Functionality {code: $functionality_code})-[:HAS_INCIDENT]->(i:Incident)
            OPTIONAL MATCH (i)-[:HAS_RESOLUTION]->(r:Resolution)
            RETURN i, r
            ORDER BY i.created_at DESC
            """
            result = self.client.query(
                query, {"functionality_code": functionality_code}
            )
            return result
        except Exception as e:
            logger.error(
                f"Error getting incidents for functionality {functionality_code}: {e}"
            )
            raise

    def get_incidents_by_product(self, product_code: str) -> List[Dict[str, Any]]:
        """Get all incidents for a specific product."""
        try:
            query = """
            MATCH (p:Product {code: $product_code})-[:ASIGNACION_FUNCIONALIDAD]->(f:Functionality)
            MATCH (f)-[:HAS_INCIDENT]->(i:Incident)
            OPTIONAL MATCH (i)-[:HAS_RESOLUTION]->(r:Resolution)
            RETURN i, r, f
            ORDER BY i.created_at DESC
            """
            result = self.client.query(query, {"product_code": product_code})
            return result
        except Exception as e:
            logger.error(f"Error getting incidents for product {product_code}: {e}")
            raise

    def get_resolutions_by_incident(self, incident_code: str) -> List[Dict[str, Any]]:
        """Get all resolutions for a specific incident."""
        try:
            query = """
            MATCH (i:Incident {code: $incident_code})-[:HAS_RESOLUTION]->(r:Resolution)
            RETURN r, i
            ORDER BY r.created_at DESC
            """
            result = self.client.query(query, {"incident_code": incident_code})
            return result
        except Exception as e:
            logger.error(f"Error getting resolutions for incident {incident_code}: {e}")
            raise

    def create_constraints(self) -> None:
        """Create database constraints for uniqueness."""
        try:
            constraints = [
                "CREATE CONSTRAINT product_code_unique IF NOT EXISTS FOR (p:Product) REQUIRE p.code IS UNIQUE",
                "CREATE CONSTRAINT functionality_code_unique IF NOT EXISTS FOR (f:Functionality) REQUIRE f.code IS UNIQUE",
                "CREATE CONSTRAINT component_code_unique IF NOT EXISTS FOR (c:Component) REQUIRE c.code IS UNIQUE",
                "CREATE CONSTRAINT incident_code_unique IF NOT EXISTS FOR (i:Incident) REQUIRE i.code IS UNIQUE",
                "CREATE CONSTRAINT resolution_incident_unique IF NOT EXISTS FOR (r:Resolution) REQUIRE r.incident_code IS UNIQUE",
            ]

            for constraint in constraints:
                self.client.query(constraint)

            logger.info("Database constraints created successfully")
        except Exception as e:
            logger.error(f"Error creating constraints: {e}")
            raise
