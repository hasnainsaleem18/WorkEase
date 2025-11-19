"""
Health Check System

Enterprise-grade health monitoring for production deployments.
Provides readiness and liveness probes for orchestration systems.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Coroutine, Optional

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: float
    metadata: dict[str, Any]


class HealthCheck:
    """
    Base class for health checks.

    Health checks verify that components are functioning correctly.
    """

    def __init__(self, name: str, timeout_seconds: float = 5.0) -> None:
        """
        Initialize health check.

        Args:
            name: Health check name
            timeout_seconds: Timeout for check execution
        """
        self.name = name
        self.timeout_seconds = timeout_seconds

    async def check(self) -> HealthCheckResult:
        """
        Execute health check.

        Returns:
            Health check result
        """
        start_time = time.time()

        try:
            # Execute check with timeout
            result = await asyncio.wait_for(
                self._execute_check(), timeout=self.timeout_seconds
            )

            duration_ms = (time.time() - start_time) * 1000

            return HealthCheckResult(
                name=self.name,
                status=result["status"],
                message=result.get("message", "OK"),
                duration_ms=duration_ms,
                timestamp=time.time(),
                metadata=result.get("metadata", {}),
            )

        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout_seconds}s",
                duration_ms=duration_ms,
                timestamp=time.time(),
                metadata={},
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                duration_ms=duration_ms,
                timestamp=time.time(),
                metadata={"error": str(e)},
            )

    async def _execute_check(self) -> dict[str, Any]:
        """
        Execute the actual health check logic.

        Returns:
            Dictionary with status and optional message/metadata

        Raises:
            Exception: If check fails
        """
        raise NotImplementedError


class DatabaseHealthCheck(HealthCheck):
    """Health check for database connectivity."""

    def __init__(self, memory_store: Any) -> None:
        """
        Initialize database health check.

        Args:
            memory_store: MemoryStore instance to check
        """
        super().__init__("database")
        self.memory_store = memory_store

    async def _execute_check(self) -> dict[str, Any]:
        """Check database connectivity."""
        if not self.memory_store.connection:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": "Database not connected",
            }

        # Try a simple query
        try:
            cursor = await self.memory_store.connection.execute("SELECT 1")
            await cursor.fetchone()
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Database connected",
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Database query failed: {str(e)}",
            }


class LLMHealthCheck(HealthCheck):
    """Health check for LLM availability."""

    def __init__(self, llm: Any) -> None:
        """
        Initialize LLM health check.

        Args:
            llm: LocalLLM instance to check
        """
        super().__init__("llm")
        self.llm = llm

    async def _execute_check(self) -> dict[str, Any]:
        """Check LLM availability."""
        try:
            # Try a simple generation
            response = await self.llm.generate("test", temperature=0.1)
            if response:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "LLM responding",
                    "metadata": {"model": self.llm.model},
                }
            else:
                return {
                    "status": HealthStatus.DEGRADED,
                    "message": "LLM returned empty response",
                }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"LLM unavailable: {str(e)}",
            }


class AgentHealthCheck(HealthCheck):
    """Health check for agent availability."""

    def __init__(self, agent_name: str, agent: Any) -> None:
        """
        Initialize agent health check.

        Args:
            agent_name: Agent name
            agent: Agent instance to check
        """
        super().__init__(f"agent_{agent_name}")
        self.agent = agent

    async def _execute_check(self) -> dict[str, Any]:
        """Check agent health."""
        if not self.agent.authenticated:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "Agent not authenticated",
            }

        return {
            "status": HealthStatus.HEALTHY,
            "message": "Agent ready",
            "metadata": {"config": self.agent.config.name},
        }


class EventBusHealthCheck(HealthCheck):
    """Health check for event bus."""

    def __init__(self, event_bus: Any) -> None:
        """
        Initialize event bus health check.

        Args:
            event_bus: EventBus instance to check
        """
        super().__init__("event_bus")
        self.event_bus = event_bus

    async def _execute_check(self) -> dict[str, Any]:
        """Check event bus health."""
        if not self.event_bus.running:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": "Event bus not running",
            }

        stats = self.event_bus.get_stats()
        queue_size = stats.get("queue_size", 0)
        max_queue_size = stats.get("max_queue_size", 1000)

        # Check if queue is getting full
        if queue_size > max_queue_size * 0.9:
            return {
                "status": HealthStatus.DEGRADED,
                "message": f"Event queue nearly full: {queue_size}/{max_queue_size}",
                "metadata": stats,
            }

        return {
            "status": HealthStatus.HEALTHY,
            "message": "Event bus running",
            "metadata": stats,
        }


class HealthCheckManager:
    """
    Manages and executes health checks.

    Provides readiness and liveness endpoints for orchestration.
    """

    def __init__(self) -> None:
        """Initialize health check manager."""
        self.checks: list[HealthCheck] = []
        self.last_results: dict[str, HealthCheckResult] = {}

    def register(self, check: HealthCheck) -> None:
        """
        Register a health check.

        Args:
            check: Health check to register
        """
        self.checks.append(check)
        logger.info(f"Health check registered: {check.name}")

    async def check_all(self) -> dict[str, Any]:
        """
        Execute all health checks.

        Returns:
            Dictionary with overall status and individual check results
        """
        results = await asyncio.gather(
            *[check.check() for check in self.checks], return_exceptions=True
        )

        # Process results
        check_results = []
        overall_status = HealthStatus.HEALTHY

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Health check failed with exception: {result}")
                overall_status = HealthStatus.UNHEALTHY
                continue

            check_results.append(result)
            self.last_results[result.name] = result

            # Determine overall status
            if result.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
            elif (
                result.status == HealthStatus.DEGRADED
                and overall_status == HealthStatus.HEALTHY
            ):
                overall_status = HealthStatus.DEGRADED

        return {
            "status": overall_status.value,
            "timestamp": time.time(),
            "checks": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "message": r.message,
                    "duration_ms": r.duration_ms,
                    "metadata": r.metadata,
                }
                for r in check_results
            ],
        }

    async def check_readiness(self) -> bool:
        """
        Check if system is ready to accept requests.

        Returns:
            True if ready, False otherwise
        """
        result = await self.check_all()
        return result["status"] in [HealthStatus.HEALTHY.value, HealthStatus.DEGRADED.value]

    async def check_liveness(self) -> bool:
        """
        Check if system is alive (basic functionality).

        Returns:
            True if alive, False otherwise
        """
        result = await self.check_all()
        return result["status"] != HealthStatus.UNHEALTHY.value

    def get_last_results(self) -> dict[str, HealthCheckResult]:
        """
        Get last health check results.

        Returns:
            Dictionary of last results by check name
        """
        return self.last_results
