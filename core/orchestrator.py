"""
Orchestrator - Central coordinator for WorkEase
Executes LLM decisions and coordinates component actions.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageSource(Enum):
    """Source of incoming messages"""

    GMAIL = "gmail"
    SLACK = "slack"
    UNKNOWN = "unknown"


@dataclass
class Message:
    """Represents an incoming message from any source"""

    id: str
    source: MessageSource
    content: str
    sender: str
    subject: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Task:
    """Represents an extracted task from a message"""

    id: str
    description: str
    source_message_id: str
    priority: int = 5  # 1-10 scale
    deadline: Optional[str] = None
    status: str = "pending"
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class MessageSummary:
    """Represents AI-generated summary of a message"""

    message_id: str
    summary: str
    key_points: List[str]
    sentiment: Optional[str] = None  # positive/negative/neutral
    urgency_level: Optional[int] = None  # 1-10 scale
    generated_at: Optional[str] = None

    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now().isoformat()


class Orchestrator:
    """
    Central orchestrator powered by LLM.

    Responsibilities:
    - Receive messages from agents (Gmail/Slack)
    - Use LLM to analyze and summarize messages
    - Extract actionable tasks using LLM reasoning
    - Coordinate with other components (future: event bus, notification hub)
    - Store results in memory/database (future integration)

    The orchestrator does NOT make decisions itself - it delegates all
    intelligence and reasoning to the LLM brain.
    """

    def __init__(self, llm_client, event_bus=None, context_provider=None):
        """
        Initialize orchestrator with dependencies.

        Args:
            llm_client: LLM client for AI reasoning (local Ollama or cloud API)
            event_bus: Event bus for pub/sub communication (optional, not implemented yet)
            context_provider: Context/memory provider (optional, not implemented yet)
        """
        self.llm = llm_client
        self.event_bus = event_bus
        self.context_provider = context_provider
        self._task_counter = 0

    async def process_message(self, message: Message) -> Dict[str, Any]:
        """
        Main entry point for processing incoming messages.

        Pipeline:
        1. Validate message
        2. Generate AI summary using LLM
        3. Extract tasks from message using LLM
        4. (Future) Publish events to event bus
        5. (Future) Store in database

        Args:
            message: Incoming message from Gmail/Slack agent

        Returns:
            Dict containing summary and extracted tasks
        """
        # Step 1: Generate summary
        summary = await self.summarize_message(message)

        # Step 2: Extract tasks
        tasks = await self.extract_tasks_from_message(message, summary)

        # Step 3: Build result
        result = {
            "message_id": message.id,
            "source": message.source.value,
            "sender": message.sender,
            "summary": summary,
            "tasks": tasks,
            "processed_at": datetime.now().isoformat(),
        }

        # Step 4: (Future) Emit events
        if self.event_bus:
            await self._emit_message_processed_event(result)

        return result

    async def summarize_message(self, message: Message) -> MessageSummary:
        """
        Generate AI-powered summary of the message using LLM.

        The LLM analyzes the message content, extracts key points,
        determines sentiment and urgency level.

        Args:
            message: Message to summarize

        Returns:
            MessageSummary with AI-generated insights
        """
        # Build prompt for LLM
        prompt = self._build_summarization_prompt(message)

        # Call LLM (this is where the AI reasoning happens)
        llm_response = await self.llm.generate(prompt)

        # Parse LLM response into structured summary
        summary = self._parse_summary_response(llm_response, message.id)

        return summary

    async def extract_tasks_from_message(
        self, message: Message, summary: MessageSummary
    ) -> List[Task]:
        """
        Extract actionable tasks from message using LLM reasoning.

        The LLM identifies action items, deadlines, and priorities
        from the message content and summary.

        Args:
            message: Original message
            summary: Pre-generated summary of the message

        Returns:
            List of extracted tasks
        """
        # Build prompt for task extraction
        prompt = self._build_task_extraction_prompt(message, summary)

        # Call LLM for task extraction reasoning
        llm_response = await self.llm.generate(prompt)

        # Parse LLM response into structured tasks
        tasks = self._parse_tasks_response(llm_response, message.id)

        return tasks

    def _build_summarization_prompt(self, message: Message) -> str:
        """
        Build prompt for LLM to summarize the message.

        Prompt engineering is critical - we tell the LLM to:
        - Extract key points
        - Determine sentiment
        - Assess urgency
        - Be concise
        """
        prompt = f"""You are the intelligent orchestrator for WorkEase, an AI communication assistant.

Your task is to analyze this {message.source.value} message and provide a comprehensive summary.

MESSAGE DETAILS:
From: {message.sender}
Subject: {message.subject or "N/A"}
Content: {message.content}

Provide your analysis in the following format:

SUMMARY: [One concise paragraph summarizing the main message]

KEY_POINTS:
- [Key point 1]
- [Key point 2]
- [Key point 3]

SENTIMENT: [positive/negative/neutral]
URGENCY: [1-10 scale, where 10 is most urgent]

Be concise but capture all important information."""

        return prompt

    def _build_task_extraction_prompt(
        self, message: Message, summary: MessageSummary
    ) -> str:
        """
        Build prompt for LLM to extract actionable tasks.

        The prompt guides the LLM to identify:
        - Clear action items
        - Deadlines/due dates
        - Priority levels
        - Task descriptions
        """
        prompt = f"""You are the WorkEase orchestrator. Your task is to extract actionable tasks from this message.

MESSAGE SUMMARY:
{summary.summary}

FULL MESSAGE CONTENT:
{message.content}

Extract all actionable tasks. For each task, provide:
1. Clear description of what needs to be done
2. Priority (1-10, where 10 is highest)
3. Deadline (if mentioned, in ISO format YYYY-MM-DD)

Format your response as:

TASKS:
- TASK: [description] | PRIORITY: [1-10] | DEADLINE: [YYYY-MM-DD or "none"]
- TASK: [description] | PRIORITY: [1-10] | DEADLINE: [YYYY-MM-DD or "none"]

If there are no actionable tasks, respond with:
TASKS: none

Only include clear, actionable items. Do not include vague or informational content."""

        return prompt

    def _parse_summary_response(
        self, llm_response: str, message_id: str
    ) -> MessageSummary:
        """
        Parse LLM response into structured MessageSummary.

        Handles various LLM response formats and extracts:
        - Summary text
        - Key points
        - Sentiment
        - Urgency level
        """
        lines = llm_response.strip().split("\n")

        summary_text = ""
        key_points = []
        sentiment = "neutral"
        urgency = 5

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("SUMMARY:"):
                summary_text = line.replace("SUMMARY:", "").strip()
                current_section = "summary"
            elif line.startswith("KEY_POINTS:"):
                current_section = "key_points"
            elif line.startswith("SENTIMENT:"):
                sentiment = line.replace("SENTIMENT:", "").strip().lower()
                current_section = None
            elif line.startswith("URGENCY:"):
                urgency_str = line.replace("URGENCY:", "").strip()
                try:
                    urgency = int(urgency_str.split()[0])  # Handle "8 out of 10" format
                except (ValueError, IndexError):
                    urgency = 5  # Default
                current_section = None
            elif line.startswith("-") and current_section == "key_points":
                key_points.append(line.lstrip("- ").strip())
            elif (
                current_section == "summary"
                and line
                and not line.startswith("KEY_POINTS")
            ):
                summary_text += " " + line

        # Fallback if parsing fails
        if not summary_text:
            summary_text = (
                llm_response[:200] + "..." if len(llm_response) > 200 else llm_response
            )

        return MessageSummary(
            message_id=message_id,
            summary=summary_text.strip(),
            key_points=key_points,
            sentiment=sentiment,
            urgency_level=urgency,
        )

    def _parse_tasks_response(self, llm_response: str, message_id: str) -> List[Task]:
        """
        Parse LLM response into structured Task objects.

        Extracts task descriptions, priorities, and deadlines
        from LLM's formatted response.
        """
        tasks = []
        lines = llm_response.strip().split("\n")

        for line in lines:
            line = line.strip()

            # Check if this is a task line
            if line.startswith("- TASK:") or line.startswith("TASK:"):
                task_data = self._parse_single_task_line(line, message_id)
                if task_data:
                    tasks.append(task_data)

        return tasks

    def _parse_single_task_line(self, line: str, message_id: str) -> Optional[Task]:
        """
        Parse a single task line from LLM response.

        Format: - TASK: [desc] | PRIORITY: [1-10] | DEADLINE: [date or "none"]
        """
        try:
            # Remove prefix
            line = line.replace("- TASK:", "").replace("TASK:", "").strip()

            # Split by |
            parts = [p.strip() for p in line.split("|")]

            if len(parts) < 2:
                return None

            description = parts[0].strip()
            priority = 5
            deadline = None

            # Parse priority
            for part in parts[1:]:
                if "PRIORITY:" in part.upper():
                    try:
                        priority = int(part.upper().replace("PRIORITY:", "").strip())
                        priority = max(1, min(10, priority))  # Clamp to 1-10
                    except ValueError:
                        priority = 5
                elif "DEADLINE:" in part.upper():
                    deadline_str = part.upper().replace("DEADLINE:", "").strip()
                    if deadline_str.lower() not in ["none", "n/a", ""]:
                        deadline = deadline_str

            # Generate task ID
            self._task_counter += 1
            task_id = f"task_{message_id}_{self._task_counter}"

            return Task(
                id=task_id,
                description=description,
                source_message_id=message_id,
                priority=priority,
                deadline=deadline,
            )

        except Exception as e:
            # Log error in production
            print(f"Warning: Failed to parse task line: {line}. Error: {e}")
            return None

    async def _emit_message_processed_event(self, result: Dict[str, Any]) -> None:
        """
        Emit event to notify other components that message was processed.

        (Future implementation when event bus is ready)
        """
        if self.event_bus:
            await self.event_bus.emit("message.processed", result)

    async def batch_process_messages(
        self, messages: List[Message]
    ) -> List[Dict[str, Any]]:
        """
        Process multiple messages concurrently.

        Useful for processing inbox backlog or batch operations.

        Args:
            messages: List of messages to process

        Returns:
            List of processing results
        """
        tasks = [self.process_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions (in production, log them)
        valid_results = [r for r in results if not isinstance(r, Exception)]

        return valid_results

    def get_stats(self) -> Dict[str, Any]:
        """
        Get orchestrator statistics.

        Returns:
            Dict with processing stats
        """
        return {
            "tasks_extracted_count": self._task_counter,
            "llm_connected": self.llm is not None,
            "event_bus_connected": self.event_bus is not None,
            "context_provider_connected": self.context_provider is not None,
        }
