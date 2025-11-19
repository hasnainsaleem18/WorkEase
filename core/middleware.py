"""
Middleware System - Request/Response Pipeline

Enterprise-grade middleware system for processing events through
a chain of handlers (like Django/FastAPI middleware).
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Optional

logger = logging.getLogger(__name__)


class Middleware(ABC):
    """
    Abstract base class for middleware components.
    
    Middleware can intercept and modify events before they reach
    handlers and responses before they're returned.
    """

    def __init__(self) -> None:
        """Initialize middleware."""
        self.next_middleware: Optional["Middleware"] = None

    @abstractmethod
    async def process_event(
        self, event: str, data: dict[str, Any], call_next: Callable
    ) -> dict[str, Any]:
        """
        Process an event through the middleware chain.

        Args:
            event: Event name
            data: Event data
            call_next: Function to call next middleware

        Returns:
            Processed event data
        """
        pass


class LoggingMiddleware(Middleware):
    """Logs all events passing through the system."""

    async def process_event(
        self, event: str, data: dict[str, Any], call_next: Callable
    ) -> dict[str, Any]:
        """Log event and pass to next middleware."""
        logger.info(f"Event received: {event}")
        logger.debug(f"Event data: {data}")

        start_time = time.time()
        result = await call_next(event, data)
        duration = time.time() - start_time

        logger.info(f"Event processed: {event} in {duration:.3f}s")
        return result


class AuthenticationMiddleware(Middleware):
    """Validates authentication tokens in events."""

    def __init__(self, required_events: Optional[list[str]] = None) -> None:
        """
        Initialize authentication middleware.

        Args:
            required_events: Events that require authentication
        """
        super().__init__()
        self.required_events = required_events or []

    async def process_event(
        self, event: str, data: dict[str, Any], call_next: Callable
    ) -> dict[str, Any]:
        """Validate authentication and pass to next middleware."""
        if event in self.required_events:
            token = data.get("auth_token")
            if not token or not self._validate_token(token):
                raise PermissionError(f"Authentication required for event: {event}")

        return await call_next(event, data)

    def _validate_token(self, token: str) -> bool:
        """
        Validate authentication token.

        Args:
            token: Authentication token

        Returns:
            True if valid
        """
        # Implement token validation logic
        return bool(token)


class RateLimitMiddleware(Middleware):
    """Rate limiting to prevent abuse."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60) -> None:
        """
        Initialize rate limit middleware.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        super().__init__()
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts: dict[str, list[float]] = {}

    async def process_event(
        self, event: str, data: dict[str, Any], call_next: Callable
    ) -> dict[str, Any]:
        """Check rate limit and pass to next middleware."""
        client_id = data.get("client_id", "default")
        current_time = time.time()

        # Initialize or clean old requests
        if client_id not in self.request_counts:
            self.request_counts[client_id] = []

        # Remove requests outside window
        self.request_counts[client_id] = [
            t
            for t in self.request_counts[client_id]
            if current_time - t < self.window_seconds
        ]

        # Check rate limit
        if len(self.request_counts[client_id]) >= self.max_requests:
            raise RuntimeError(
                f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds}s"
            )

        # Add current request
        self.request_counts[client_id].append(current_time)

        return await call_next(event, data)


class CachingMiddleware(Middleware):
    """Caches event responses for performance."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        """
        Initialize caching middleware.

        Args:
            ttl_seconds: Time-to-live for cache entries
        """
        super().__init__()
        self.ttl_seconds = ttl_seconds
        self.cache: dict[str, tuple[dict[str, Any], float]] = {}

    async def process_event(
        self, event: str, data: dict[str, Any], call_next: Callable
    ) -> dict[str, Any]:
        """Check cache or pass to next middleware."""
        # Create cache key
        cache_key = f"{event}:{hash(frozenset(data.items()))}"
        current_time = time.time()

        # Check cache
        if cache_key in self.cache:
            cached_result, cached_time = self.cache[cache_key]
            if current_time - cached_time < self.ttl_seconds:
                logger.debug(f"Cache hit for event: {event}")
                return cached_result

        # Call next middleware
        result = await call_next(event, data)

        # Store in cache
        self.cache[cache_key] = (result, current_time)

        return result


class ErrorHandlingMiddleware(Middleware):
    """Catches and handles errors gracefully."""

    async def process_event(
        self, event: str, data: dict[str, Any], call_next: Callable
    ) -> dict[str, Any]:
        """Wrap event processing in error handling."""
        try:
            return await call_next(event, data)
        except Exception as e:
            logger.error(f"Error processing event {event}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "event": event,
            }


class MetricsMiddleware(Middleware):
    """Collects metrics for monitoring."""

    def __init__(self) -> None:
        """Initialize metrics middleware."""
        super().__init__()
        self.metrics: dict[str, dict[str, Any]] = {}

    async def process_event(
        self, event: str, data: dict[str, Any], call_next: Callable
    ) -> dict[str, Any]:
        """Collect metrics and pass to next middleware."""
        if event not in self.metrics:
            self.metrics[event] = {
                "count": 0,
                "total_time": 0.0,
                "errors": 0,
                "last_called": None,
            }

        start_time = time.time()
        try:
            result = await call_next(event, data)
            duration = time.time() - start_time

            self.metrics[event]["count"] += 1
            self.metrics[event]["total_time"] += duration
            self.metrics[event]["last_called"] = time.time()

            return result
        except Exception as e:
            self.metrics[event]["errors"] += 1
            raise

    def get_metrics(self) -> dict[str, dict[str, Any]]:
        """
        Get collected metrics.

        Returns:
            Dictionary of metrics by event
        """
        return {
            event: {
                **stats,
                "avg_time": (
                    stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
                ),
            }
            for event, stats in self.metrics.items()
        }


class MiddlewareStack:
    """
    Manages middleware chain execution.

    Middleware are executed in order, with each middleware
    able to modify the event or short-circuit the chain.
    """

    def __init__(self) -> None:
        """Initialize middleware stack."""
        self.middlewares: list[Middleware] = []

    def add(self, middleware: Middleware) -> None:
        """
        Add middleware to the stack.

        Args:
            middleware: Middleware instance to add
        """
        self.middlewares.append(middleware)
        logger.info(f"Middleware added: {middleware.__class__.__name__}")

    async def execute(
        self,
        event: str,
        data: dict[str, Any],
        final_handler: Callable[[str, dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]],
    ) -> dict[str, Any]:
        """
        Execute middleware chain.

        Args:
            event: Event name
            data: Event data
            final_handler: Final handler to call after all middleware

        Returns:
            Processed result
        """

        async def build_chain(index: int) -> Callable:
            """Build middleware chain recursively."""
            if index >= len(self.middlewares):
                # End of chain, call final handler
                return final_handler

            middleware = self.middlewares[index]
            next_handler = await build_chain(index + 1)

            async def handler(evt: str, dt: dict[str, Any]) -> dict[str, Any]:
                return await middleware.process_event(evt, dt, next_handler)

            return handler

        # Build and execute chain
        chain = await build_chain(0)
        return await chain(event, data)


# Pre-configured middleware stacks for common use cases
def create_production_stack() -> MiddlewareStack:
    """
    Create production-ready middleware stack.

    Returns:
        Configured middleware stack
    """
    stack = MiddlewareStack()
    stack.add(LoggingMiddleware())
    stack.add(MetricsMiddleware())
    stack.add(ErrorHandlingMiddleware())
    stack.add(RateLimitMiddleware(max_requests=1000, window_seconds=60))
    stack.add(CachingMiddleware(ttl_seconds=300))
    return stack


def create_development_stack() -> MiddlewareStack:
    """
    Create development middleware stack.

    Returns:
        Configured middleware stack
    """
    stack = MiddlewareStack()
    stack.add(LoggingMiddleware())
    stack.add(ErrorHandlingMiddleware())
    return stack
