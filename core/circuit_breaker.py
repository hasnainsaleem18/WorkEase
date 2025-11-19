"""
Circuit Breaker Pattern

Enterprise resilience pattern to prevent cascading failures.
Automatically stops calling failing services and retries after cooldown.
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """
    Circuit breaker for resilient service calls.

    Prevents cascading failures by stopping calls to failing services
    and allowing them time to recover.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: float = 60.0,
        half_open_timeout: float = 30.0,
    ) -> None:
        """
        Initialize circuit breaker.

        Args:
            name: Circuit breaker name
            failure_threshold: Failures before opening circuit
            success_threshold: Successes in half-open before closing
            timeout_seconds: Time to wait before trying again
            half_open_timeout: Timeout for half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_timeout = half_open_timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()

    async def call(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
        """
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Retry after {self._time_until_retry():.1f}s"
                )

        try:
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Record success
            self._on_success()
            return result

        except Exception as e:
            # Record failure
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.info(
                f"Circuit breaker '{self.name}': Success in HALF_OPEN "
                f"({self.success_count}/{self.success_threshold})"
            )

            if self.success_count >= self.success_threshold:
                self._transition_to_closed()
        else:
            # Reset failure count on success in CLOSED state
            self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        logger.warning(
            f"Circuit breaker '{self.name}': Failure "
            f"({self.failure_count}/{self.failure_threshold})"
        )

        if self.state == CircuitState.HALF_OPEN:
            # Immediately open on failure in half-open
            self._transition_to_open()
        elif self.failure_count >= self.failure_threshold:
            # Open circuit after threshold failures
            self._transition_to_open()

    def _should_attempt_reset(self) -> bool:
        """
        Check if enough time has passed to attempt reset.

        Returns:
            True if should attempt reset
        """
        if not self.last_failure_time:
            return False

        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.timeout_seconds

    def _time_until_retry(self) -> float:
        """
        Calculate time until retry is allowed.

        Returns:
            Seconds until retry
        """
        if not self.last_failure_time:
            return 0.0

        time_since_failure = time.time() - self.last_failure_time
        return max(0.0, self.timeout_seconds - time_since_failure)

    def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        self.state = CircuitState.OPEN
        self.last_state_change = time.time()
        logger.error(
            f"Circuit breaker '{self.name}' transitioned to OPEN. "
            f"Will retry after {self.timeout_seconds}s"
        )

    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.last_state_change = time.time()
        logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN")

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = time.time()
        logger.info(f"Circuit breaker '{self.name}' transitioned to CLOSED")

    def get_state(self) -> dict[str, Any]:
        """
        Get current circuit breaker state.

        Returns:
            Dictionary with state information
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "time_in_state": time.time() - self.last_state_change,
            "time_until_retry": self._time_until_retry() if self.state == CircuitState.OPEN else 0,
        }

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        self._transition_to_closed()
        logger.info(f"Circuit breaker '{self.name}' manually reset")


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers.

    Provides centralized circuit breaker management for all services.
    """

    def __init__(self) -> None:
        """Initialize circuit breaker manager."""
        self.breakers: dict[str, CircuitBreaker] = {}

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: float = 60.0,
    ) -> CircuitBreaker:
        """
        Get existing or create new circuit breaker.

        Args:
            name: Circuit breaker name
            failure_threshold: Failures before opening
            success_threshold: Successes before closing
            timeout_seconds: Timeout before retry

        Returns:
            Circuit breaker instance
        """
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                success_threshold=success_threshold,
                timeout_seconds=timeout_seconds,
            )
            logger.info(f"Created circuit breaker: {name}")

        return self.breakers[name]

    def get_all_states(self) -> dict[str, dict[str, Any]]:
        """
        Get states of all circuit breakers.

        Returns:
            Dictionary of circuit breaker states
        """
        return {name: breaker.get_state() for name, breaker in self.breakers.items()}

    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for breaker in self.breakers.values():
            breaker.reset()
        logger.info("All circuit breakers reset")


# Global circuit breaker manager
_global_manager: Optional[CircuitBreakerManager] = None


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """
    Get global circuit breaker manager.

    Returns:
        Global manager instance
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = CircuitBreakerManager()
    return _global_manager


# Decorator for circuit breaker
def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    success_threshold: int = 2,
    timeout_seconds: float = 60.0,
) -> Callable:
    """
    Decorator to wrap function with circuit breaker.

    Args:
        name: Circuit breaker name
        failure_threshold: Failures before opening
        success_threshold: Successes before closing
        timeout_seconds: Timeout before retry

    Returns:
        Decorator function

    Example:
        @circuit_breaker("gmail_api", failure_threshold=3, timeout_seconds=30)
        async def fetch_emails():
            # API call
            pass
    """

    def decorator(func: Callable) -> Callable:
        manager = get_circuit_breaker_manager()
        breaker = manager.get_or_create(
            name, failure_threshold, success_threshold, timeout_seconds
        )

        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator
