"""
Task Extraction Algorithm

Extracts actionable tasks from message content.
Works in conjunction with LLM analysis to identify and structure tasks.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Tuple


class TaskPriority(Enum):
    """Task priority levels"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class ExtractedTask:
    """Represents an extracted task"""

    description: str
    priority: TaskPriority
    deadline: Optional[datetime] = None
    confidence: float = 0.0
    source_text: str = ""


class TaskExtractor:
    """
    Extracts actionable tasks from message text.
    Uses pattern matching and keyword detection to identify tasks.
    Designed to work with LLM-generated summaries and raw messages.
    """

    # Action verbs that typically indicate tasks
    ACTION_VERBS = {
        "send",
        "email",
        "write",
        "draft",
        "prepare",
        "create",
        "make",
        "complete",
        "finish",
        "submit",
        "review",
        "check",
        "update",
        "schedule",
        "arrange",
        "organize",
        "plan",
        "coordinate",
        "call",
        "contact",
        "reach out",
        "follow up",
        "get back",
        "upload",
        "download",
        "share",
        "distribute",
        "deliver",
        "test",
        "verify",
        "validate",
        "confirm",
        "approve",
        "fix",
        "resolve",
        "handle",
        "address",
        "investigate",
    }

    # Modal verbs indicating obligation/necessity (higher weight = more urgent)
    MODAL_VERBS = {
        "must": 0.9,
        "need to": 0.85,
        "have to": 0.85,
        "should": 0.7,
        "ought to": 0.7,
        "need": 0.75,
        "required to": 0.9,
        "supposed to": 0.6,
        "expected to": 0.65,
        "please": 0.5,
    }

    # Urgency keywords (impact priority calculation)
    URGENCY_KEYWORDS = {
        "urgent": 0.9,
        "asap": 0.95,
        "immediately": 0.95,
        "critical": 0.9,
        "important": 0.75,
        "priority": 0.8,
        "emergency": 1.0,
        "deadline": 0.85,
        "today": 0.9,
        "now": 0.95,
        "quickly": 0.7,
        "soon": 0.6,
    }

    # Time expressions for deadline extraction
    TIME_PATTERNS = [
        (r"by\s+(\w+day)", "by_weekday"),
        (r"by\s+end\s+of\s+day", "eod"),
        (r"by\s+eod", "eod"),
        (r"by\s+(\d{1,2})\s*(am|pm)", "by_time"),
        (r"today", "today"),
        (r"tomorrow", "tomorrow"),
        (r"this\s+week", "this_week"),
        (r"next\s+week", "next_week"),
        (r"in\s+(\d+)\s+(hour|day|week)s?", "relative"),
        (r"(\d{1,2})/(\d{1,2})", "date"),
        (r"(\w+)\s+(\d{1,2})", "month_day"),
    ]

    def __init__(self):
        """Initialize task extractor"""
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), ptype)
            for pattern, ptype in self.TIME_PATTERNS
        ]

    def extract_tasks(
        self, text: str, llm_analysis: Optional[dict] = None
    ) -> List[ExtractedTask]:
        """
        Extract tasks from text.

        Args:
            text: The message content or summary
            llm_analysis: Optional LLM analysis result with pre-identified tasks

        Returns:
            List of extracted tasks with priorities and deadlines
        """
        tasks = []

        # If LLM already extracted tasks, structure them
        if llm_analysis and "tasks" in llm_analysis:
            for llm_task in llm_analysis["tasks"]:
                task = self._structure_llm_task(llm_task, text)
                if task:
                    tasks.append(task)

        # Also do pattern-based extraction as backup/supplement
        pattern_tasks = self._extract_by_patterns(text)

        # Merge and deduplicate tasks
        tasks = self._merge_tasks(tasks, pattern_tasks)

        return tasks

    def _structure_llm_task(
        self, llm_task: str, original_text: str
    ) -> Optional[ExtractedTask]:
        """
        Structure a task identified by LLM with priority and deadline.

        Args:
            llm_task: Task description from LLM
            original_text: Original message text

        Returns:
            Structured ExtractedTask or None
        """
        if not llm_task or not llm_task.strip():
            return None

        # Clean task description
        description = llm_task.strip().strip("-•*").strip()

        # Calculate priority from text analysis
        priority = self._calculate_priority(description, original_text)

        # Extract deadline if mentioned
        deadline = self._extract_deadline(original_text)

        # Calculate confidence (high for LLM-identified tasks)
        confidence = 0.85

        return ExtractedTask(
            description=description,
            priority=priority,
            deadline=deadline,
            confidence=confidence,
            source_text=original_text[:100],
        )

    def _extract_by_patterns(self, text: str) -> List[ExtractedTask]:
        """
        Extract tasks using pattern matching (backup method).

        Args:
            text: Message text

        Returns:
            List of extracted tasks
        """
        tasks = []
        sentences = re.split(r"[.!?]\s+", text)

        for sentence in sentences:
            if self._is_task_sentence(sentence):
                priority = self._calculate_priority(sentence, text)
                deadline = self._extract_deadline(sentence)
                confidence = self._calculate_confidence(sentence)

                task = ExtractedTask(
                    description=sentence.strip(),
                    priority=priority,
                    deadline=deadline,
                    confidence=confidence,
                    source_text=sentence,
                )
                tasks.append(task)

        return tasks

    def _is_task_sentence(self, sentence: str) -> bool:
        """
        Check if sentence likely contains a task.

        Args:
            sentence: Text to analyze

        Returns:
            True if sentence appears to contain a task
        """
        sentence_lower = sentence.lower()

        # Check for action verbs
        has_action = any(verb in sentence_lower for verb in self.ACTION_VERBS)

        # Check for modal verbs
        has_modal = any(modal in sentence_lower for modal in self.MODAL_VERBS)

        # Check for command form (imperative)
        starts_with_action = any(
            sentence_lower.strip().startswith(verb) for verb in self.ACTION_VERBS
        )

        return has_action or has_modal or starts_with_action

    def _calculate_priority(self, task_text: str, full_context: str) -> TaskPriority:
        """
        Calculate task priority based on keywords and context.

        Args:
            task_text: The task description
            full_context: Full message context

        Returns:
            TaskPriority level
        """
        score = 0.0
        combined_text = (task_text + " " + full_context).lower()

        # Check for modal verbs (obligation)
        for modal, weight in self.MODAL_VERBS.items():
            if modal in combined_text:
                score += weight

        # Check for urgency keywords
        for keyword, weight in self.URGENCY_KEYWORDS.items():
            if keyword in combined_text:
                score += weight

        # Check for deadline mentions
        if self._has_deadline_mention(combined_text):
            score += 0.5

        # Normalize score and map to priority
        if score >= 1.5:
            return TaskPriority.URGENT
        elif score >= 1.0:
            return TaskPriority.HIGH
        elif score >= 0.5:
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.LOW

    def _has_deadline_mention(self, text: str) -> bool:
        """Check if text mentions a deadline"""
        deadline_indicators = ["deadline", "by", "before", "due", "until"]
        return any(indicator in text.lower() for indicator in deadline_indicators)

    def _extract_deadline(self, text: str) -> Optional[datetime]:
        """
        Extract deadline from text using pattern matching.

        Args:
            text: Text to search for deadline

        Returns:
            Datetime of deadline or None
        """
        text_lower = text.lower()
        now = datetime.now()

        for pattern, ptype in self.compiled_patterns:
            match = pattern.search(text_lower)
            if match:
                return self._parse_deadline_match(match, ptype, now)

        return None

    def _parse_deadline_match(
        self, match: re.Match, pattern_type: str, reference_time: datetime
    ) -> Optional[datetime]:
        """
        Parse deadline from regex match based on pattern type.

        Args:
            match: Regex match object
            pattern_type: Type of time pattern matched
            reference_time: Current time for relative calculations

        Returns:
            Parsed datetime or None
        """
        try:
            if pattern_type == "eod":
                return reference_time.replace(hour=17, minute=0, second=0)

            elif pattern_type == "today":
                return reference_time.replace(hour=23, minute=59, second=59)

            elif pattern_type == "tomorrow":
                return (reference_time + timedelta(days=1)).replace(hour=23, minute=59)

            elif pattern_type == "this_week":
                days_until_friday = (4 - reference_time.weekday()) % 7
                return (reference_time + timedelta(days=days_until_friday)).replace(
                    hour=17, minute=0
                )

            elif pattern_type == "next_week":
                days_until_next_monday = (7 - reference_time.weekday()) % 7
                return (
                    reference_time + timedelta(days=days_until_next_monday + 7)
                ).replace(hour=17, minute=0)

            elif pattern_type == "relative":
                amount = int(match.group(1))
                unit = match.group(2)
                if unit.startswith("hour"):
                    return reference_time + timedelta(hours=amount)
                elif unit.startswith("day"):
                    return reference_time + timedelta(days=amount)
                elif unit.startswith("week"):
                    return reference_time + timedelta(weeks=amount)

            elif pattern_type == "by_time":
                hour = int(match.group(1))
                period = match.group(2).lower()
                if period == "pm" and hour != 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                return reference_time.replace(hour=hour, minute=0, second=0)

        except (ValueError, AttributeError):
            pass

        return None

    def _calculate_confidence(self, sentence: str) -> float:
        """
        Calculate confidence that this is actually a task.

        Args:
            sentence: Sentence to analyze

        Returns:
            Confidence score 0.0-1.0
        """
        confidence = 0.0
        sentence_lower = sentence.lower()

        # Action verb presence
        if any(verb in sentence_lower for verb in self.ACTION_VERBS):
            confidence += 0.4

        # Modal verb presence
        if any(modal in sentence_lower for modal in self.MODAL_VERBS):
            confidence += 0.3

        # Urgency keyword presence
        if any(keyword in sentence_lower for keyword in self.URGENCY_KEYWORDS):
            confidence += 0.2

        # Deadline mention
        if self._has_deadline_mention(sentence_lower):
            confidence += 0.1

        return min(confidence, 1.0)

    def _merge_tasks(
        self, llm_tasks: List[ExtractedTask], pattern_tasks: List[ExtractedTask]
    ) -> List[ExtractedTask]:
        """
        Merge LLM-extracted and pattern-extracted tasks, removing duplicates.

        Args:
            llm_tasks: Tasks from LLM analysis
            pattern_tasks: Tasks from pattern matching

        Returns:
            Merged list without duplicates
        """
        # Prefer LLM tasks, add pattern tasks if they're different
        merged = list(llm_tasks)

        for pattern_task in pattern_tasks:
            is_duplicate = any(
                self._tasks_similar(pattern_task, existing_task)
                for existing_task in merged
            )
            if not is_duplicate:
                merged.append(pattern_task)

        return merged

    def _tasks_similar(self, task1: ExtractedTask, task2: ExtractedTask) -> bool:
        """
        Check if two tasks are similar (for deduplication).

        Args:
            task1: First task
            task2: Second task

        Returns:
            True if tasks are similar
        """
        desc1 = task1.description.lower()
        desc2 = task2.description.lower()

        # Simple similarity: check if one contains the other or significant overlap
        if desc1 in desc2 or desc2 in desc1:
            return True

        # Check word overlap
        words1 = set(desc1.split())
        words2 = set(desc2.split())
        overlap = len(words1 & words2)

        # If more than 60% words overlap, consider similar
        min_length = min(len(words1), len(words2))
        if min_length > 0 and overlap / min_length > 0.6:
            return True

        return False
