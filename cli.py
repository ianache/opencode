"""
Production-ready CLI interface for GraphRAG application.

Provides command-line interface with health checks,
performance monitoring, and enhanced error handling.
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import get_settings
from data.processor import DataProcessor
from graph.neo4j_client import create_neo4j_client
from utils.health import HealthChecker
from utils.logging import setup_logger
from utils.performance import OperationTimer, get_performance_monitor


def run_data_processing(args):
    """Run data processing workflow."""
    logger = setup_logger("graphrag")
    monitor = get_performance_monitor()

    with OperationTimer("data_processing_workflow"):
        try:
            logger.info("Starting data processing workflow")

            # Initialize processor
            processor = DataProcessor()

            # Load data
            logger.info("Loading news data...")
            data = processor.load_news_data()

            # Clean data
            logger.info("Cleaning and processing data...")
            cleaned_data = processor.clean_text_data(data)

            # Get summary
            summary = processor.get_data_summary(cleaned_data)
            logger.info(f"Processing completed: {summary['total_articles']} articles")

            # Display results
            print(f"\nData Processing Results:")
            print(f"Total articles: {summary['total_articles']}")
            print(f"Columns: {summary['columns']}")
            print(f"Missing values: {summary['missing_values']}")

            # Performance summary
            perf_summary = monitor.get_summary()
            print(f"\nPerformance Summary:")
            print(f"Total operations: {perf_summary['total_operations']}")
            print(f"Success rate: {perf_summary['success_rate']:.2%}")
            if "average_duration" in perf_summary:
                print(f"Average duration: {perf_summary['average_duration']:.3f}s")

            return True

        except Exception as e:
            logger.error(f"Data processing workflow failed: {e}")
            return False


def run_health_check(args):
    """Run health check."""
    logger = setup_logger("health")

    try:
        health_checker = HealthChecker()

        if args.component:
            # Check specific component
            if args.component == "database":
                status = health_checker.check_database_health()
            elif args.component == "data_processing":
                status = health_checker.check_data_processing_health()
            elif args.component == "configuration":
                status = health_checker.check_configuration_health()
            elif args.component == "system":
                status = health_checker.check_system_health()
            else:
                print(f"Unknown component: {args.component}")
                print(
                    "Available components: database, data_processing, configuration, system"
                )
                return False

            print(f"\nComponent: {status.component}")
            print(f"Status: {status.status}")
            print(f"Message: {status.message}")
            if status.response_time:
                print(f"Response Time: {status.response_time:.3f}s")

        else:
            # Check all components
            health_checker.print_health_status()

        return True

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


def run_database_query(args):
    """Run database query and display results."""
    logger = setup_logger("database")

    if not args.query:
        print("Error: --query argument is required for database query")
        return False

    try:
        with OperationTimer("database_query"):
            with create_neo4j_client() as client:
                logger.info(f"Executing query: {args.query}")
                results = client.query(args.query)

                print(f"\nQuery Results:")
                print(f"Query: {args.query}")
                print(f"Records returned: {len(results)}")

                if results:
                    print("\nResults:")
                    for i, record in enumerate(results, 1):
                        print(f"{i}. {record}")
                else:
                    print("No results returned")

        return True

    except Exception as e:
        logger.error(f"Database query failed: {e}")
        return False


def show_performance_metrics(args):
    """Display performance metrics."""
    monitor = get_performance_monitor()
    metrics = monitor.get_metrics()
    summary = monitor.get_summary()

    print("\nPerformance Metrics:")
    print("=" * 50)

    if not metrics:
        print("No performance metrics recorded")
        return

    # Show summary
    print(f"Total Operations: {summary['total_operations']}")
    print(f"Successful: {summary['successful_operations']}")
    print(f"Failed: {summary['failed_operations']}")
    print(f"Success Rate: {summary['success_rate']:.2%}")

    if "average_duration" in summary:
        print(f"Average Duration: {summary['average_duration']:.3f}s")
        print(f"Min Duration: {summary['min_duration']:.3f}s")
        print(f"Max Duration: {summary['max_duration']:.3f}s")
        print(f"Total Duration: {summary['total_duration']:.3f}s")

    # Show individual metrics
    print(f"\nIndividual Operations:")
    for name, metric in metrics.items():
        status = "✅" if metric.success else "❌"
        print(f"{status} {name}")
        print(
            f"   Duration: {metric.duration:.3f}s"
            if metric.duration
            else "   Duration: N/A"
        )
        if metric.error_message:
            print(f"   Error: {metric.error_message}")

    print("=" * 50)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GraphRAG - Graph Retrieval-Augmented Generation Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s process                    # Run data processing workflow
  %(prog)s health                     # Check health of all components
  %(prog)s health --component database # Check specific component
  %(prog)s query --query "MATCH (n) RETURN count(n)" # Run database query
  %(prog)s metrics                    # Show performance metrics
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Data processing command
    process_parser = subparsers.add_parser(
        "process", help="Run data processing workflow"
    )
    process_parser.set_defaults(func=run_data_processing)

    # Health check command
    health_parser = subparsers.add_parser("health", help="Check system health")
    health_parser.add_argument(
        "--component",
        choices=["database", "data_processing", "configuration", "system"],
        help="Check specific component (default: all)",
    )
    health_parser.set_defaults(func=run_health_check)

    # Database query command
    query_parser = subparsers.add_parser("query", help="Run database query")
    query_parser.add_argument("--query", required=True, help="Cypher query to execute")
    query_parser.set_defaults(func=run_database_query)

    # Performance metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Show performance metrics")
    metrics_parser.set_defaults(func=show_performance_metrics)

    # Parse arguments
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    # Show application info
    settings = get_settings()
    print(f"GraphRAG Application v{settings.app_name}")
    print(f"Neo4j URI: {settings.neo4j_uri}")
    print()

    # Execute command
    try:
        success = args.func(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
