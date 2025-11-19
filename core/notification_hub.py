"""
Notification Hub - Central Notification Management

Manages all notifications with priority queuing, smart filtering,
quiet hours, and multi-channel delivery (UI, TTS, pop-ups).
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from typing import Any, Optional

from core.event_bus import EventBus

logger = logging.getLogger(__name__)


class Priority(str, Enum):
    """Notification priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType(str, Enum):
    """Types of notifications."""

    MESSAGE = "message"
    ALERT = "alert"
    REMINDER = "reminder"
    DIGEST = "digest"
    SYSTEM = "system"


@dataclass
class Notification:
    """Structured notification object."""

    id: str
    title: str
    body: str
    priority: Priority
    notification_type: NotificationType
    source: str  # "gmail", "slack", "system"
    timestamp: datetime
    actions: list[str]  # Available quick actions
    metadata: dict[str, Any]  # Additional data


class NotificationHub:
    """
    Central hub for managing all system notifications.

    Handles priority queuing, quiet hours filtering, and
    multi-channel delivery to UI, TTS, and pop-ups.
    """

    def __init__(
        self,
        event_bus: EventBus,
        quiet_hours_start: time,
        quiet_hours_end: time,
        urgent_override: bool = True,
    ) -> None:
        """
        Initialize the notification hub.

        Args:
            event_bus: Event bus for notification delivery
            quiet_hours_start: Start time for quiet hours
            quiet_hours_end: End time for quiet hours
            urgent_override: Allow urgent notifications during quiet hours
        """
        self.event_bus = event_bus
        self.quiet_hours_start = quiet_hours_start
        self.quiet_hours_end = quiet_hours_end
        self.urgent_override = urgent_override
        self.queued_notifications: list[Notification] = []
        self.notification_history: list[Notification] = []

    async def handle_notification(self, notification: Notification) -> None:
        """
        Process an incoming notification.

        Args:
            notification: Notification to process
        """
        try:
            # Check if should be suppressed
            if self._should_suppress(notification):
                logger.info(f"Notification queued during quiet hours: {notification.id}")
                await self._queue_for_later(notification)
                return

            # Deliver immediately
            await self._deliver(notification)

            # Store in history
            self.notification_history.append(notification)

        except Exception as e:
            logger.error(f"Error handling notification: {e}", exc_info=True)

    def _should_suppress(self, notification: Notification) -> bool:
        """
        Determine if notification should be suppressed.

        Args:
            notification: Notification to check

        Returns:
            True if should be suppressed, False otherwise
        """
        # Check if in quiet hours
        if not self._is_quiet_hours():
            return False

        # Check urgent override
        if self.urgent_override and notification.priority == Priority.URGENT:
            return False

        return True

    def _is_quiet_hours(self) -> bool:
        """
        Check if current time is within quiet hours.

        Returns:
            True if in quiet hours, False otherwise
        """
        current_time = datetime.now().time()

        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if self.quiet_hours_start > self.quiet_hours_end:
            return current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end
        else:
            return self.quiet_hours_start <= current_time <= self.quiet_hours_end

    async def _queue_for_later(self, notification: Notification) -> None:
        """
        Queue notification for delivery after quiet hours.

        Args:
            notification: Notification to queue
        """
        self.queued_notifications.append(notification)

    async def _deliver(self, notification: Notification) -> None:
        """
        Deliver notification through appropriate channels.

        Args:
            notification: Notification to deliver
        """
        # Emit to UI
        await self.event_bus.emit(
            "ui.notification",
            {
                "notification": notification,
                "show_popup": notification.priority in [Priority.HIGH, Priority.URGENT],
            },
        )

        # Emit to TTS for urgent/high priority
        if notification.priority in [Priority.HIGH, Priority.URGENT]:
            await self.event_bus.emit(
                "voice.speak",
                {"text": f"{notification.title}. {notification.body}", "priority": notification.priority.value},
            )

        logger.info(f"Notification delivered: {notification.id} ({notification.priority})")

    async def deliver_queued_notifications(self) -> None:
        """Deliver all queued notifications after quiet hours end."""
        if not self.queued_notifications:
            return

        logger.info(f"Delivering {len(self.queued_notifications)} queued notifications")

        # Create summary
        summary = self._create_queued_summary()
        await self.event_bus.emit("ui.notification", {"notification": summary})

        # Deliver individual notifications
        for notification in self.queued_notifications:
            await self._deliver(notification)
            await asyncio.sleep(0.5)  # Throttle delivery

        self.queued_notifications.clear()

    def _create_queued_summary(self) -> Notification:
        """
        Create a summary notification for queued items.

        Returns:
            Summary notification
        """
        count = len(self.queued_notifications)
        sources = set(n.source for n in self.queued_notifications)

        return Notification(
            id=f"summary_{datetime.now().timestamp()}",
            title="Missed Notifications",
            body=f"You have {count} notifications from {', '.join(sources)}",
            priority=Priority.NORMAL,
            notification_type=NotificationType.SYSTEM,
            source="system",
            timestamp=datetime.now(),
            actions=["view_all", "dismiss"],
            metadata={"count": count, "sources": list(sources)},
        )

    async def get_notification_history(self, limit: int = 50) -> list[Notification]:
        """
        Retrieve recent notification history.

        Args:
            limit: Maximum number of notifications to return

        Returns:
            List of recent notifications
        """
        return self.notification_history[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """
        Get notification hub statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "queued_count": len(self.queued_notifications),
            "history_count": len(self.notification_history),
            "in_quiet_hours": self._is_quiet_hours(),
            "urgent_override": self.urgent_override,
        }
