"""
Async Event Bus for Inter-Component Communication

Implements a pub/sub pattern using asyncio queues for decoupled
communication between orchestrator, agents, UI, and voice pipeline.
"""

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)


class EventBus:
    """
    Asynchronous event bus for publish-subscribe messaging.

    Components can subscribe to specific event types and publish
    events that will be delivered to all subscribers.
    """

    def __init__(self, max_queue_size: int = 1000) -> None:
        """
        Initialize the event bus.

        Args:
            max_queue_size: Maximum number of events in queue before backpressure
        """
        self.subscribers: dict[str, list[Callable[..., Coroutine[Any, Any, None]]]] = (
            defaultdict(list)
        )
        self.queue: asyncio.Queue[tuple[str, dict[str, Any]]] = asyncio.Queue(
            maxsize=max_queue_size
        )
        self.running = False
        self._task: asyncio.Task[None] | None = None

    async def emit(self, event: str, data: dict[str, Any]) -> None:
        """
        Publish an event to the bus.

        Args:
            event: Event type identifier
            data: Event payload

        Raises:
            asyncio.QueueFull: If queue is at max capacity
        """
        try:
            await self.queue.put((event, data))
            logger.debug(f"Event emitted: {event} with data: {data}")
        except asyncio.QueueFull:
            logger.error(f"Event queue full, dropping event: {event}")
            raise

    async def subscribe(
        self, event: str, handler: Callable[..., Coroutine[Any, Any, None]]
    ) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event: Event type to subscribe to
            handler: Async function to call when event occurs
        """
        self.subscribers[event].append(handler)
        logger.info(f"Handler subscribed to event: {event}")

    async def unsubscribe(
        self, event: str, handler: Callable[..., Coroutine[Any, Any, None]]
    ) -> None:
        """
        Unsubscribe a handler from an event type.

        Args:
            event: Event type to unsubscribe from
            handler: Handler function to remove
        """
        if event in self.subscribers and handler in self.subscribers[event]:
            self.subscribers[event].remove(handler)
            logger.info(f"Handler unsubscribed from event: {event}")

    async def start(self) -> None:
        """Start the event bus processing loop."""
        if self.running:
            logger.warning("Event bus already running")
            return

        self.running = True
        self._task = asyncio.create_task(self._process_events())
        logger.info("Event bus started")

    async def stop(self) -> None:
        """Stop the event bus and wait for pending events."""
        if not self.running:
            return

        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Event bus stopped")

    async def _process_events(self) -> None:
        """
        Internal event processing loop.

        Continuously processes events from the queue and dispatches
        them to registered handlers.
        """
        while self.running:
            try:
                event, data = await asyncio.wait_for(self.queue.get(), timeout=1.0)

                if event in self.subscribers:
                    # Dispatch to all subscribers concurrently
                    tasks = [
                        self._safe_handler_call(handler, data)
                        for handler in self.subscribers[event]
                    ]
                    await asyncio.gather(*tasks, return_exceptions=True)
                else:
                    logger.warning(f"No subscribers for event: {event}")

                self.queue.task_done()

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)

    async def _safe_handler_call(
        self, handler: Callable[..., Coroutine[Any, Any, None]], data: dict[str, Any]
    ) -> None:
        """
        Call a handler with error isolation.

        Args:
            handler: Handler function to call
            data: Event data to pass to handler
        """
        try:
            await handler(data)
        except Exception as e:
            logger.error(
                f"Handler {handler.__name__} failed: {e}", exc_info=True
            )

    def get_stats(self) -> dict[str, Any]:
        """
        Get event bus statistics.

        Returns:
            Dictionary with queue size and subscriber counts
        """
        return {
            "queue_size": self.queue.qsize(),
            "max_queue_size": self.queue.maxsize,
            "running": self.running,
            "subscribers": {
                event: len(handlers) for event, handlers in self.subscribers.items()
            },
        }
