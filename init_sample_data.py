#!/usr/bin/env python3
"""
Initialize Neo4j database with sample data for testing MCP server.
"""

import os
from graph.neo4j_client import create_neo4j_client
from graph.product_manager import ProductManager
from loguru import logger


def create_sample_data():
    """Create sample products and functionalities for testing."""
    try:
        # Initialize Neo4j client
        client = create_neo4j_client()
        manager = ProductManager(client)

        logger.info("Creating sample data...")

        # Create some functionalities first
        functionalities = [
            ("REPORTES", "Report Generation"),
            ("CONTABILIDAD", "Capacity Management"),
            ("GESTION", "Resource Management"),
            ("ANALISIS", "Data Analysis"),
            ("MONITOREO", "System Monitoring"),
        ]

        for func_code, func_name in functionalities:
            try:
                result = manager.create_functionality(func_code, func_name)
                if result:
                    logger.info(f"Created functionality: {func_code}")
                else:
                    logger.warning(f"Failed to create functionality: {func_code}")
            except Exception as e:
                logger.error(f"Error creating functionality {func_code}: {e}")

        # Create some products
        products = [
            ("ERP", "ERP System", ["REPORTES", "CONTABILIDAD", "GESTION"]),
            ("CRM", "CRM System", ["ANALISIS", "MONITOREO"]),
            ("SCM", "Supply Chain Management", ["GESTION"]),
            ("BI", "Business Intelligence", ["REPORTES", "ANALISIS"]),
        ]

        for prod_code, prod_name, func_codes in products:
            try:
                # Create product
                product_result = manager.create_product(prod_code, prod_name)
                if product_result:
                    logger.info(f"Created product: {prod_code}")

                    # Assign functionalities to product
                    for func_code in func_codes:
                        assign_result = manager.assign_functionality_to_product(
                            prod_code, func_code
                        )
                        if assign_result:
                            logger.info(
                                f"Assigned functionality {func_code} to product {prod_code}"
                            )
                        else:
                            logger.warning(
                                f"Failed to assign functionality {func_code} to product {prod_code}"
                            )
                else:
                    logger.warning(f"Failed to create product: {prod_code}")
            except Exception as e:
                logger.error(f"Error creating product {prod_code}: {e}")

        logger.info("Sample data creation completed")
        return True

    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        return False


def main():
    """Initialize database with sample data."""
    logger.info("Starting database initialization...")

    success = create_sample_data()

    if success:
        logger.info("Database initialized successfully with sample data")
        print("✅ Sample data created successfully!")
        print("\nAvailable products:")
        print("- ERP: ERP System")
        print("- CRM: CRM System")
        print("- SCM: Supply Chain Management")
        print("- BI: Business Intelligence")
        print("\nYou can now test these products with the MCP server.")
    else:
        logger.error("Failed to initialize database")
        print("❌ Failed to create sample data")


if __name__ == "__main__":
    main()
