"""
Task Extractor - NLP-based Actionable Item Detection

Analyzes messages to identify and extract actionable tasks
with priority ranking and context preservation.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Extracted task representation."""

    id: str
    title: str
    description: str
    priority: str  # "low", "normal", "high", "urgent"
    source: str  # "gmail", "slack"
    source_message_id: str
    source_sender: str
    extracted_at: datetime
    completed: bool = False
    due_date: Optional[datetime] = None


class TaskExtractor:
    """
    Extracts actionable tasks from messages using NLP and pattern matching.

    Uses both LLM-based extraction and rule-based fallbacks for reliability.
    """

    # Task indicator keywords
    TASK_KEYWORDS = [
        "todo",
        "to do",
        "task",
        "action item",
        "please",
        "could you",
        "can you",
        "need to",
        "should",
        "must",
        "required",
        "deadline",
        "by tomorrow",
        "asap",
        "urgent",
    ]

    # Urgency indicators
    URGENCY_KEYWORDS = {
        "urgent": 10,
        "asap": 10,
        "immediately": 10,
        "critical": 9,
        "important": 8,
        "priority": 7,
        "soon": 6,
        "today": 7,
        "tomorrow": 5,
        "this week": 4,
    }

    def __init__(self, llm: Any) -> None:
        """
        Initialize the task extractor.

        Args:
            llm: Local LLM instance for advanced extraction
        """
        self.llm = llm
        self.extracted_tasks: list[Task] = []

    async def extract_from_message(
        self, message_text: str, source: str, message_id: str, sender: str
    ) -> Optional[Task]:
        """
        Extract task from a message.

        Args:
            message_text: Message content
            source: Source service ("gmail", "slack")
            message_id: Unique message identifier
            sender: Message sender

        Returns:
            Extracted Task or None if no task found
        """
        try:
            # First, check if message likely contains a task
            if not self._contains_task_indicators(message_text):
                return None

            # Try LLM extraction
            task_data = await self.llm.extract_task(message_text)

            if task_data and task_data.get("title"):
                # Calculate priority
                priority = self._calculate_priority(message_text, task_data.get("priority", "normal"))

                task = Task(
                    id=f"{source}_{message_id}_{datetime.now().timestamp()}",
                    title=task_data["title"],
                    description=task_data.get("description", message_text[:200]),
                    priority=priority,
                    source=source,
                    source_message_id=message_id,
                    source_sender=sender,
                    extracted_at=datetime.now(),
                )

                self.extracted_tasks.append(task)
                logger.info(f"Task extracted: {task.title} (priority: {task.priority})")
                return task

            # Fallback to rule-based extraction
            return self._rule_based_extraction(message_text, source, message_id, sender)

        except Exception as e:
            logger.error(f"Error extracting task: {e}", exc_info=True)
            return None

    def _contains_task_indicators(self, text: str) -> bool:
        """
        Check if text contains task indicator keywords.

        Args:
            text: Text to analyze

        Returns:
            True if task indicators found
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.TASK_KEYWORDS)

    def _calculate_priority(self, text: str, llm_priority: str) -> str:
        """
        Calculate task priority based on text analysis.

        Args:
            text: Message text
            llm_priority: Priority suggested by LLM

        Returns:
            Final priority level
        """
        text_lower = text.lower()
        urgency_score = 0

        # Check for urgency keywords
        for keyword, score in self.URGENCY_KEYWORDS.items():
            if keyword in text_lower:
                urgency_score = max(urgency_score, score)

        # Map score to priority
        if urgency_score >= 9:
            return "urgent"
        elif urgency_score >= 7:
            return "high"
        elif urgency_score >= 4:
            return "normal"
        else:
            # Use LLM suggestion if no strong indicators
            return llm_priority

    def _rule_based_extraction(
        self, text: str, source: str, message_id: str, sender: str
    ) -> Optional[Task]:
        """
        Fallback rule-based task extraction.

        Args:
            text: Message text
            source: Source service
            message_id: Message ID
            sender: Sender name

        Returns:
            Extracted Task or None
        """
        # Extract first sentence as title
        sentences = re.split(r"[.!?]", text)
        title = sentences[0].strip() if sentences else text[:50]

        # Simple priority detection
        priority = self._calculate_priority(text, "normal")

        task = Task(
            id=f"{source}_{message_id}_{datetime.now().timestamp()}",
            title=title,
            description=text[:200],
            priority=priority,
            source=source,
            source_message_id=message_id,
            source_sender=sender,
            extracted_at=datetime.now(),
        )

        self.extracted_tasks.append(task)
        return task

    def get_prioritized_tasks(self, limit: int = 10, include_completed: bool = False) -> list[Task]:
        """
        Get tasks sorted by priority.

        Args:
            limit: Maximum number of tasks to return
            include_completed: Include completed tasks

        Returns:
            List of prioritized tasks
        """
        # Filter tasks
        tasks = self.extracted_tasks
        if not include_completed:
            tasks = [t for t in tasks if not t.completed]

        # Sort by priority
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        sorted_tasks = sorted(tasks, key=lambda t: (priority_order.get(t.priority, 4), t.extracted_at))

        return sorted_tasks[:limit]

    def mark_task_completed(self, task_id: str) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: Task identifier

        Returns:
            True if task found and marked, False otherwise
        """
        for task in self.extracted_tasks:
            if task.id == task_id:
                task.completed = True
                logger.info(f"Task marked completed: {task.title}")
                return True
        return False

    def get_task_stats(self) -> dict[str, Any]:
        """
        Get task extraction statistics.

        Returns:
            Dictionary with stats
        """
        total = len(self.extracted_tasks)
        completed = sum(1 for t in self.extracted_tasks if t.completed)
        by_priority = {}

        for task in self.extracted_tasks:
            if not task.completed:
                by_priority[task.priority] = by_priority.get(task.priority, 0) + 1

        return {
            "total_extracted": total,
            "completed": completed,
            "pending": total - completed,
            "by_priority": by_priority,
        }
