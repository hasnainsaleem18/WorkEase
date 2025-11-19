"""
Digest Generator - Automated Communication Summaries

Generates daily and weekly summaries of communications from Gmail and Slack
with categorization and action item extraction.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class Digest:
    """Communication digest summary."""

    id: str
    period: str  # "daily", "weekly", "custom"
    start_time: datetime
    end_time: datetime
    summary: str
    message_count: int
    by_source: dict[str, int]  # {"gmail": 10, "slack": 25}
    by_sender: dict[str, int]  # Top senders
    action_items: list[str]
    urgent_count: int
    generated_at: datetime


class DigestGenerator:
    """
    Generates automated communication digests.

    Creates summaries of messages from specified time periods
    with categorization, statistics, and action item extraction.
    """

    def __init__(self, llm: Any, memory_store: Any, task_extractor: Any) -> None:
        """
        Initialize the digest generator.

        Args:
            llm: Local LLM for summarization
            memory_store: Memory store for message retrieval
            task_extractor: Task extractor for action items
        """
        self.llm = llm
        self.memory_store = memory_store
        self.task_extractor = task_extractor
        self.generated_digests: list[Digest] = []

    async def generate_digest(
        self,
        period: str = "daily",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Digest:
        """
        Generate a communication digest.

        Args:
            period: Digest period ("daily", "weekly", "custom")
            start_time: Start time (defaults to period-based)
            end_time: End time (defaults to now)

        Returns:
            Generated Digest
        """
        try:
            # Determine time range
            if not end_time:
                end_time = datetime.now()

            if not start_time:
                if period == "daily":
                    start_time = end_time - timedelta(days=1)
                elif period == "weekly":
                    start_time = end_time - timedelta(weeks=1)
                else:
                    start_time = end_time - timedelta(days=1)

            logger.info(f"Generating {period} digest from {start_time} to {end_time}")

            # Fetch messages from memory store
            messages = await self._fetch_messages(start_time, end_time)

            if not messages:
                return self._create_empty_digest(period, start_time, end_time)

            # Categorize messages
            by_source, by_sender = self._categorize_messages(messages)

            # Extract action items
            action_items = await self._extract_action_items(messages)

            # Count urgent messages
            urgent_count = sum(
                1 for msg in messages if msg.get("priority") in ["high", "urgent"]
            )

            # Generate summary using LLM
            summary = await self._generate_summary(messages, period)

            # Create digest
            digest = Digest(
                id=f"digest_{datetime.now().timestamp()}",
                period=period,
                start_time=start_time,
                end_time=end_time,
                summary=summary,
                message_count=len(messages),
                by_source=by_source,
                by_sender=by_sender,
                action_items=action_items,
                urgent_count=urgent_count,
                generated_at=datetime.now(),
            )

            self.generated_digests.append(digest)
            logger.info(f"Digest generated: {len(messages)} messages, {len(action_items)} action items")

            return digest

        except Exception as e:
            logger.error(f"Error generating digest: {e}", exc_info=True)
            return self._create_empty_digest(period, start_time or datetime.now(), end_time or datetime.now())

    async def _fetch_messages(
        self, start_time: datetime, end_time: datetime
    ) -> list[dict[str, Any]]:
        """
        Fetch messages from memory store.

        Args:
            start_time: Start time
            end_time: End time

        Returns:
            List of messages
        """
        # In real implementation, query memory store with time range
        # For now, return empty list (will be implemented with actual message storage)
        return []

    def _categorize_messages(
        self, messages: list[dict[str, Any]]
    ) -> tuple[dict[str, int], dict[str, int]]:
        """
        Categorize messages by source and sender.

        Args:
            messages: List of messages

        Returns:
            Tuple of (by_source, by_sender) dictionaries
        """
        by_source: dict[str, int] = {}
        by_sender: dict[str, int] = {}

        for msg in messages:
            source = msg.get("source", "unknown")
            sender = msg.get("sender", "unknown")

            by_source[source] = by_source.get(source, 0) + 1
            by_sender[sender] = by_sender.get(sender, 0) + 1

        # Get top 5 senders
        top_senders = dict(
            sorted(by_sender.items(), key=lambda x: x[1], reverse=True)[:5]
        )

        return by_source, top_senders

    async def _extract_action_items(
        self, messages: list[dict[str, Any]]
    ) -> list[str]:
        """
        Extract action items from messages.

        Args:
            messages: List of messages

        Returns:
            List of action item descriptions
        """
        action_items = []

        for msg in messages:
            text = msg.get("text", "") or msg.get("body", "")
            if not text:
                continue

            # Use task extractor
            task = await self.task_extractor.extract_from_message(
                text,
                msg.get("source", "unknown"),
                msg.get("id", ""),
                msg.get("sender", ""),
            )

            if task:
                action_items.append(task.title)

        return action_items[:10]  # Return top 10

    async def _generate_summary(
        self, messages: list[dict[str, Any]], period: str
    ) -> str:
        """
        Generate natural language summary using LLM.

        Args:
            messages: List of messages
            period: Digest period

        Returns:
            Summary text
        """
        # Build context for LLM
        message_snippets = []
        for msg in messages[:20]:  # Limit to 20 for context size
            text = msg.get("text", "") or msg.get("body", "")
            sender = msg.get("sender", "Unknown")
            source = msg.get("source", "unknown")
            message_snippets.append(f"[{source}] {sender}: {text[:100]}")

        context = "\n".join(message_snippets)

        prompt = f"""Summarize the following {period} communications in 3-4 sentences.
Focus on key topics, important updates, and overall themes.

Messages:
{context}

Summary:"""

        try:
            summary = await self.llm.generate(prompt)
            # Clean up and limit length
            summary = summary.strip()
            if len(summary) > 500:
                summary = summary[:497] + "..."
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Summary of {len(messages)} messages from the past {period}."

    def _create_empty_digest(
        self, period: str, start_time: datetime, end_time: datetime
    ) -> Digest:
        """
        Create an empty digest when no messages found.

        Args:
            period: Digest period
            start_time: Start time
            end_time: End time

        Returns:
            Empty Digest
        """
        return Digest(
            id=f"digest_{datetime.now().timestamp()}",
            period=period,
            start_time=start_time,
            end_time=end_time,
            summary=f"No messages received during this {period} period.",
            message_count=0,
            by_source={},
            by_sender={},
            action_items=[],
            urgent_count=0,
            generated_at=datetime.now(),
        )

    def format_digest_text(self, digest: Digest) -> str:
        """
        Format digest as readable text.

        Args:
            digest: Digest to format

        Returns:
            Formatted text
        """
        lines = [
            f"=== {digest.period.upper()} DIGEST ===",
            f"Period: {digest.start_time.strftime('%Y-%m-%d %H:%M')} to {digest.end_time.strftime('%Y-%m-%d %H:%M')}",
            f"Total Messages: {digest.message_count}",
            "",
            "Summary:",
            digest.summary,
            "",
        ]

        if digest.by_source:
            lines.append("By Source:")
            for source, count in digest.by_source.items():
                lines.append(f"  - {source}: {count}")
            lines.append("")

        if digest.by_sender:
            lines.append("Top Senders:")
            for sender, count in digest.by_sender.items():
                lines.append(f"  - {sender}: {count}")
            lines.append("")

        if digest.action_items:
            lines.append("Action Items:")
            for item in digest.action_items:
                lines.append(f"  - {item}")
            lines.append("")

        if digest.urgent_count > 0:
            lines.append(f"Urgent Messages: {digest.urgent_count}")

        return "\n".join(lines)

    def get_recent_digests(self, limit: int = 5) -> list[Digest]:
        """
        Get recently generated digests.

        Args:
            limit: Maximum number of digests

        Returns:
            List of recent digests
        """
        return self.generated_digests[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """
        Get digest generator statistics.

        Returns:
            Dictionary with stats
        """
        total = len(self.generated_digests)
        total_messages = sum(d.message_count for d in self.generated_digests)
        total_actions = sum(len(d.action_items) for d in self.generated_digests)

        return {
            "total_digests": total,
            "total_messages_summarized": total_messages,
            "total_action_items": total_actions,
            "avg_messages_per_digest": total_messages / total if total > 0 else 0,
        }
