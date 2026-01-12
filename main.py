"""
Main entry point for GraphRAG application.

Demonstrates the modular architecture with secure
configuration management and proper error handling.
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger

from config.settings import get_settings
from data.processor import DataProcessor
from data.sample_data import SampleDataLoader
from graph.neo4j_client import Neo4jClient, create_neo4j_client
from graph.product_manager import ProductManager


def demo_feature1(neo4j_client: Neo4jClient) -> None:
    """Demonstrate Feature 1: Product Management functionality."""
    print("\n" + "=" * 60)
    print("FEATURE 1 DEMO: PRODUCT MANAGEMENT IN NEO4J")
    print("=" * 60)

    try:
        # Initialize ProductManager
        product_manager = ProductManager(neo4j_client)
        sample_loader = SampleDataLoader(product_manager)

        # Load sample data
        print("\n📦 Loading sample data...")
        summary = sample_loader.load_all_sample_data()
        print(f"✅ Sample data loaded: {summary}")

        # Show products summary
        print("\n📊 Products Summary:")
        products_summary = product_manager.get_all_products_summary()
        for item in products_summary:
            print(f"  • {item['product_code']}: {item['product_name']}")
            print(
                f"    Functionalities: {item['functionality_count']}, Incidents: {item['incident_count']}"
            )

        # Show detailed example
        print("\n🔍 Detailed Example - ERP Product:")
        erp_details = product_manager.get_product_with_functionalities("ERP")
        if erp_details:
            product = erp_details.get("p", {})
            functionalities = erp_details.get("functionalities", [])
            incidents = erp_details.get("incidents", [])

            print(f"  Product: {product.get('code')} - {product.get('name')}")
            print(f"  Functionalities ({len(functionalities)}):")
            for func in functionalities:
                print(f"    • {func.get('code')}: {func.get('name')}")

            if incidents:
                print(f"  Incidents ({len(incidents)}):")
                for incident in incidents:
                    print(
                        f"    • {incident.get('code')}: {incident.get('sla_level')} - {incident.get('description')[:50]}..."
                    )

        # Show functionality example
        print("\n🔧 Functionality Example - Reportes:")
        reportes_details = product_manager.get_functionality_with_products("REPORTES")
        if reportes_details:
            functionality = reportes_details.get("f", {})
            products = reportes_details.get("products", [])
            incidents = reportes_details.get("incidents", [])

            print(
                f"  Functionality: {functionality.get('code')} - {functionality.get('name')}"
            )
            print(
                f"  Used in products ({len(products)}): {', '.join([p.get('code', 'N/A') for p in products])}"
            )
            print(f"  Related incidents: {len(incidents)}")

        # Show component example
        print("\n⚙️ Component Example - Frontend Web:")
        frontend_details = product_manager.get_component_with_functionalities(
            "FRONTEND_WEB"
        )
        if frontend_details:
            component = frontend_details.get("c", {})
            functionalities = frontend_details.get("functionalities", [])

            print(f"  Component: {component.get('code')} - {component.get('name')}")
            print(f"  Assigned functionalities ({len(functionalities)}):")
            for func in functionalities:
                print(f"    • {func.get('code')}: {func.get('name')}")

        print("\n🎯 Feature 1 Demo completed successfully!")

    except Exception as e:
        print(f"❌ Error in Feature 1 demo: {e}")
        logger.error(f"Feature 1 demo error: {e}")
        raise


def run_original_demo(neo4j_client: Neo4jClient) -> None:
    """Run the original news data processing demo."""
    print("\n📰 Running original news data processing demo...")

    # Process news data
    data_processor = DataProcessor()
    news_data = data_processor.load_news_data()

    # Clean the data
    cleaned_data = data_processor.clean_text_data(news_data)

    # Get data summary
    summary = data_processor.get_data_summary(cleaned_data)

    # Display results
    print("\nNews Data Summary:")
    print(f"Total articles: {summary['total_articles']}")
    print(f"Columns: {summary['columns']}")
    print(f"Missing values: {summary['missing_values']}")

    print("\nSample articles:")
    for i, article in enumerate(summary["sample_articles"], 1):
        print(f"{i}. {article['title'][:50]}...")

    logger.info(f"Successfully processed {summary['total_articles']} articles")


def main() -> None:
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="GraphRAG Application")
    parser.add_argument(
        "--feature1", action="store_true", help="Run Feature 1: Product Management demo"
    )
    parser.add_argument(
        "--load-sample", action="store_true", help="Load sample data for Feature 1"
    )
    parser.add_argument(
        "--clear-data", action="store_true", help="Clear all sample data"
    )

    args = parser.parse_args()

    print("Starting GraphRAG Application...")

    # Get application settings
    settings = get_settings()
    print(f"Settings: {settings}")

    logger.info("Application started")

    # Initialize components
    try:
        # Create Neo4j client and connect
        with create_neo4j_client() as neo4j_client:
            logger.info("Neo4j client initialized and connected")

            # Get database schema information
            try:
                schema = neo4j_client.get_schema()
                print(f"\nDatabase Schema:\n{schema}")
                logger.info("Database schema retrieved")
            except Exception as e:
                logger.warning(f"Could not retrieve schema: {e}")

            # Handle command line arguments
            if args.feature1:
                demo_feature1(neo4j_client)
            elif args.load_sample:
                product_manager = ProductManager(neo4j_client)
                sample_loader = SampleDataLoader(product_manager)
                summary = sample_loader.load_all_sample_data()
                print(f"✅ Sample data loaded: {summary}")
            elif args.clear_data:
                product_manager = ProductManager(neo4j_client)
                sample_loader = SampleDataLoader(product_manager)
                sample_loader.clear_all_data()
                print("✅ All sample data cleared")
            else:
                # Run original demo by default
                run_original_demo(neo4j_client)

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

    print("\nGraphRAG Application completed successfully")


if __name__ == "__main__":
    main()
