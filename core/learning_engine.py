"""
Learning Engine - Adaptive User Preference Learning

Tracks user interactions and learns preferences for personalization
including tone, priorities, and communication patterns.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LearningEngine:
    """
    Adaptive learning system for user preference tracking.

    Learns from user interactions to improve personalization:
    - Preferred communication tones
    - Important senders and topics
    - Response patterns
    - Priority preferences
    """

    def __init__(self, memory_store: Any) -> None:
        """
        Initialize the learning engine.

        Args:
            memory_store: Memory store for persistence
        """
        self.memory_store = memory_store
        self.sender_preferences: dict[str, dict[str, Any]] = defaultdict(dict)
        self.tone_preferences: dict[str, int] = defaultdict(int)
        self.priority_senders: set[str] = set()
        self.ignored_senders: set[str] = set()
        self.interaction_count = 0

    async def initialize(self) -> None:
        """Load learned preferences from storage."""
        try:
            # Load from memory store
            prefs = await self.memory_store.get_preference("learning_engine")
            if prefs:
                data = json.loads(prefs)
                self.sender_preferences = defaultdict(dict, data.get("sender_preferences", {}))
                self.tone_preferences = defaultdict(int, data.get("tone_preferences", {}))
                self.priority_senders = set(data.get("priority_senders", []))
                self.ignored_senders = set(data.get("ignored_senders", []))
                self.interaction_count = data.get("interaction_count", 0)
                logger.info("Learning engine preferences loaded")
        except Exception as e:
            logger.warning(f"Could not load preferences: {e}")

    async def save_preferences(self) -> None:
        """Persist learned preferences to storage."""
        try:
            data = {
                "sender_preferences": dict(self.sender_preferences),
                "tone_preferences": dict(self.tone_preferences),
                "priority_senders": list(self.priority_senders),
                "ignored_senders": list(self.ignored_senders),
                "interaction_count": self.interaction_count,
                "last_updated": datetime.now().isoformat(),
            }
            await self.memory_store.set_preference("learning_engine", json.dumps(data))
            logger.debug("Learning engine preferences saved")
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")

    async def learn_from_interaction(
        self, sender: str, action: str, metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Learn from a user interaction.

        Args:
            sender: Message sender
            action: User action ("reply", "ignore", "archive", "priority")
            metadata: Additional interaction data
        """
        self.interaction_count += 1

        # Update sender preferences
        if sender not in self.sender_preferences:
            self.sender_preferences[sender] = {
                "reply_count": 0,
                "ignore_count": 0,
                "archive_count": 0,
                "priority_count": 0,
                "first_seen": datetime.now().isoformat(),
            }

        # Increment action counter
        action_key = f"{action}_count"
        if action_key in self.sender_preferences[sender]:
            self.sender_preferences[sender][action_key] += 1

        self.sender_preferences[sender]["last_interaction"] = datetime.now().isoformat()

        # Update priority senders
        if action == "priority" or self.sender_preferences[sender]["reply_count"] > 5:
            self.priority_senders.add(sender)

        # Update ignored senders
        if self.sender_preferences[sender]["ignore_count"] > 3:
            self.ignored_senders.add(sender)

        # Save periodically
        if self.interaction_count % 10 == 0:
            await self.save_preferences()

        logger.debug(f"Learned from interaction: {sender} -> {action}")

    async def learn_from_edit(self, original: str, edited: str, tone: str) -> None:
        """
        Learn from draft edits.

        Args:
            original: Original draft text
            edited: Edited version
            tone: Draft tone
        """
        # Analyze edit patterns (simplified)
        if len(edited) < len(original):
            # User prefers shorter responses
            self.tone_preferences[f"{tone}_shorter"] += 1
        elif len(edited) > len(original):
            # User prefers longer responses
            self.tone_preferences[f"{tone}_longer"] += 1

        logger.debug(f"Learned from edit: {tone}")

    async def learn_from_rejection(self, tone: str, reason: Optional[str]) -> None:
        """
        Learn from draft rejections.

        Args:
            tone: Rejected draft tone
            reason: Optional rejection reason
        """
        self.tone_preferences[f"{tone}_rejected"] += 1
        logger.debug(f"Learned from rejection: {tone}")

    async def get_preferred_tone(self, sender: str) -> Optional[str]:
        """
        Get preferred tone for a sender.

        Args:
            sender: Sender email

        Returns:
            Preferred tone or None
        """
        if sender in self.sender_preferences:
            prefs = self.sender_preferences[sender]
            # If user frequently replies, use friendly tone
            if prefs.get("reply_count", 0) > 3:
                return "friendly"
            # If marked as priority, use professional tone
            if sender in self.priority_senders:
                return "professional"

        return None

    def is_priority_sender(self, sender: str) -> bool:
        """
        Check if sender is marked as priority.

        Args:
            sender: Sender email

        Returns:
            True if priority sender
        """
        return sender in self.priority_senders

    def is_ignored_sender(self, sender: str) -> bool:
        """
        Check if sender should be ignored.

        Args:
            sender: Sender email

        Returns:
            True if should be ignored
        """
        return sender in self.ignored_senders

    async def add_priority_sender(self, sender: str) -> None:
        """
        Manually add a priority sender.

        Args:
            sender: Sender email
        """
        self.priority_senders.add(sender)
        await self.learn_from_interaction(sender, "priority")
        logger.info(f"Added priority sender: {sender}")

    async def remove_priority_sender(self, sender: str) -> None:
        """
        Remove a priority sender.

        Args:
            sender: Sender email
        """
        self.priority_senders.discard(sender)
        await self.save_preferences()
        logger.info(f"Removed priority sender: {sender}")

    def get_sender_stats(self, sender: str) -> Optional[dict[str, Any]]:
        """
        Get interaction statistics for a sender.

        Args:
            sender: Sender email

        Returns:
            Statistics dictionary or None
        """
        return self.sender_preferences.get(sender)

    def get_top_senders(self, limit: int = 10) -> list[tuple[str, int]]:
        """
        Get most frequently interacted senders.

        Args:
            limit: Maximum number of senders

        Returns:
            List of (sender, interaction_count) tuples
        """
        sender_counts = [
            (sender, prefs.get("reply_count", 0) + prefs.get("priority_count", 0))
            for sender, prefs in self.sender_preferences.items()
        ]
        sender_counts.sort(key=lambda x: x[1], reverse=True)
        return sender_counts[:limit]

    def get_learning_stats(self) -> dict[str, Any]:
        """
        Get learning engine statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "total_interactions": self.interaction_count,
            "tracked_senders": len(self.sender_preferences),
            "priority_senders": len(self.priority_senders),
            "ignored_senders": len(self.ignored_senders),
            "tone_preferences": dict(self.tone_preferences),
        }
