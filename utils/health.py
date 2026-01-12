"""
Health check utilities for GraphRAG application.

Provides health status monitoring for different
components and services.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from config.settings import get_settings
from data.processor import DataProcessor
from graph.neo4j_client import create_neo4j_client
from utils.logging import get_logger


@dataclass
class HealthStatus:
    """Health status data structure."""

    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    response_time: Optional[float] = None
    last_check: float
    details: Dict[str, Any] = None


class HealthChecker:
    """Health checking utility."""

    def __init__(self):
        self.logger = get_logger("health")
        self.settings = get_settings()

    def check_database_health(self) -> HealthStatus:
        """Check Neo4j database health."""
        start_time = time.time()

        try:
            with create_neo4j_client() as client:
                # Simple connectivity test
                result = client.query("RETURN 1 as test")
                response_time = time.time() - start_time

                if result and result[0].get("test") == 1:
                    return HealthStatus(
                        component="database",
                        status="healthy",
                        message="Database connection successful",
                        response_time=response_time,
                        last_check=time.time(),
                        details={"uri": self.settings.neo4j_uri},
                    )
                else:
                    return HealthStatus(
                        component="database",
                        status="unhealthy",
                        message="Database query returned unexpected result",
                        response_time=response_time,
                        last_check=time.time(),
                    )

        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                component="database",
                status="unhealthy",
                message=f"Database connection failed: {str(e)}",
                response_time=response_time,
                last_check=time.time(),
                details={"error": str(e)},
            )

    def check_data_processing_health(self) -> HealthStatus:
        """Check data processing capabilities."""
        start_time = time.time()

        try:
            processor = DataProcessor()

            # Test data loading (small sample)
            import pandas as pd

            test_data = pd.DataFrame(
                {
                    "title": ["Test Article"],
                    "date": ["2024-01-01"],
                    "text": ["Test content for health check"],
                }
            )

            # Test data validation
            processor._validate_news_data(test_data)

            # Test data cleaning
            cleaned_data = processor.clean_text_data(test_data)

            response_time = time.time() - start_time

            if len(cleaned_data) > 0:
                return HealthStatus(
                    component="data_processing",
                    status="healthy",
                    message="Data processing functions working correctly",
                    response_time=response_time,
                    last_check=time.time(),
                    details={
                        "test_records_processed": len(cleaned_data),
                        "data_url": self.settings.news_data_url,
                    },
                )
            else:
                return HealthStatus(
                    component="data_processing",
                    status="degraded",
                    message="Data processing completed but no records remain",
                    response_time=response_time,
                    last_check=time.time(),
                )

        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                component="data_processing",
                status="unhealthy",
                message=f"Data processing failed: {str(e)}",
                response_time=response_time,
                last_check=time.time(),
                details={"error": str(e)},
            )

    def check_configuration_health(self) -> HealthStatus:
        """Check configuration health."""
        start_time = time.time()

        try:
            # Validate critical settings
            missing_vars = []
            if not self.settings.neo4j_uri.strip():
                missing_vars.append("NEO4J_URI")
            if not self.settings.neo4j_username.strip():
                missing_vars.append("NEO4J_USERNAME")
            if not self.settings.neo4j_password.strip():
                missing_vars.append("NEO4J_PASSWORD")

            response_time = time.time() - start_time

            if not missing_vars:
                return HealthStatus(
                    component="configuration",
                    status="healthy",
                    message="All required configuration variables are set",
                    response_time=response_time,
                    last_check=time.time(),
                    details={
                        "app_name": self.settings.app_name,
                        "log_level": self.settings.log_level,
                    },
                )
            else:
                return HealthStatus(
                    component="configuration",
                    status="unhealthy",
                    message=f"Missing required configuration: {', '.join(missing_vars)}",
                    response_time=response_time,
                    last_check=time.time(),
                    details={"missing_variables": missing_vars},
                )

        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                component="configuration",
                status="unhealthy",
                message=f"Configuration check failed: {str(e)}",
                response_time=response_time,
                last_check=time.time(),
                details={"error": str(e)},
            )

    def check_system_health(self) -> HealthStatus:
        """Check overall system health."""
        start_time = time.time()

        try:
            import psutil

            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            response_time = time.time() - start_time

            # Determine status based on resource usage
            if cpu_percent > 90 or memory.percent > 90:
                status = "degraded"
                message = f"High resource usage - CPU: {cpu_percent}%, Memory: {memory.percent}%"
            else:
                status = "healthy"
                message = "System resources within acceptable limits"

            return HealthStatus(
                component="system",
                status=status,
                message=message,
                response_time=response_time,
                last_check=time.time(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3),
                    "disk_usage_percent": (disk.used / disk.total) * 100,
                },
            )

        except ImportError:
            # psutil not available
            response_time = time.time() - start_time
            return HealthStatus(
                component="system",
                status="healthy",
                message="System health check skipped (psutil not available)",
                response_time=response_time,
                last_check=time.time(),
                details={"psutil_available": False},
            )
        except Exception as e:
            response_time = time.time() - start_time
            return HealthStatus(
                component="system",
                status="unhealthy",
                message=f"System health check failed: {str(e)}",
                response_time=response_time,
                last_check=time.time(),
                details={"error": str(e)},
            )

    def get_overall_health(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        health_checks = [
            self.check_configuration_health(),
            self.check_database_health(),
            self.check_data_processing_health(),
            self.check_system_health(),
        ]

        # Determine overall status
        statuses = [check.status for check in health_checks]
        if all(status == "healthy" for status in statuses):
            overall_status = "healthy"
        elif any(status == "unhealthy" for status in statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"

        return {
            "overall_status": overall_status,
            "timestamp": time.time(),
            "checks": {
                check.component: {
                    "status": check.status,
                    "message": check.message,
                    "response_time": check.response_time,
                    "details": check.details,
                }
                for check in health_checks
            },
            "summary": {
                "total_checks": len(health_checks),
                "healthy_checks": len([s for s in statuses if s == "healthy"]),
                "degraded_checks": len([s for s in statuses if s == "degraded"]),
                "unhealthy_checks": len([s for s in statuses if s == "unhealthy"]),
            },
        }

    def print_health_status(self) -> None:
        """Print formatted health status."""
        health = self.get_overall_health()

        print("\n" + "=" * 50)
        print(f"GRAPHRAG HEALTH STATUS: {health['overall_status'].upper()}")
        print("=" * 50)

        for component, check_info in health["checks"].items():
            status_symbol = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}.get(
                check_info["status"], "❓"
            )

            print(f"\n{status_symbol} {component.upper()}")
            print(f"   Status: {check_info['status']}")
            print(f"   Message: {check_info['message']}")

            if check_info["response_time"]:
                print(f"   Response Time: {check_info['response_time']:.3f}s")

            if check_info["details"]:
                for key, value in check_info["details"].items():
                    if isinstance(value, float):
                        print(f"   {key}: {value:.3f}")
                    else:
                        print(f"   {key}: {value}")

        print(f"\nSUMMARY")
        print(f"   Total Checks: {health['summary']['total_checks']}")
        print(f"   Healthy: {health['summary']['healthy_checks']}")
        print(f"   Degraded: {health['summary']['degraded_checks']}")
        print(f"   Unhealthy: {health['summary']['unhealthy_checks']}")
        print("=" * 50)
