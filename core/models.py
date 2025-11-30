"""
Data Models for AutoReturn
Defines core data structures used throughout the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageSource(Enum):
    """Source platform for messages"""

    GMAIL = "gmail"
    SLACK = "slack"
    UNKNOWN = "unknown"


class SentimentType(Enum):
    """Sentiment classification"""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ToneType(Enum):
    """Message tone classification"""

    URGENT = "urgent"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class TaskStatus(Enum):
    """Task completion status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Message:
    """
    Represents an incoming message from Gmail or Slack.
    This is the raw message received from agents before processing.
    """

    id: str
    source: MessageSource
    content: str
    sender: str
    subject: Optional[str] = None
    timestamp: Optional[str] = None
    thread_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set default timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

        # Convert string source to enum if needed
        if isinstance(self.source, str):
            self.source = MessageSource(self.source.lower())

    def validate(self) -> bool:
        """Validate message data integrity"""
        if not self.id or not self.content or not self.sender:
            return False
        if self.source not in MessageSource:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "source": self.source.value,
            "content": self.content,
            "sender": self.sender,
            "subject": self.subject,
            "timestamp": self.timestamp,
            "thread_id": self.thread_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            source=MessageSource(data["source"]),
            content=data["content"],
            sender=data["sender"],
            subject=data.get("subject"),
            timestamp=data.get("timestamp"),
            thread_id=data.get("thread_id"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class MessageAnalysis:
    """
    Result of LLM analysis on a message.
    Contains AI-generated insights about the message.
    """

    message_id: str
    summary: str
    sentiment: SentimentType
    sentiment_score: float  # -1.0 to 1.0
    urgency_level: int  # 0-10 scale
    priority_score: int  # 0-100 scale
    tone: ToneType
    extracted_tasks: List["Task"] = field(default_factory=list)
    requires_response: bool = False
    suggested_response_time: Optional[str] = None  # e.g., "within 2 hours"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Convert string enums if needed"""
        if isinstance(self.sentiment, str):
            self.sentiment = SentimentType(self.sentiment.lower())
        if isinstance(self.tone, str):
            self.tone = ToneType(self.tone.lower())

    def validate(self) -> bool:
        """Validate analysis data"""
        if not self.message_id or not self.summary:
            return False
        if not (-1.0 <= self.sentiment_score <= 1.0):
            return False
        if not (0 <= self.urgency_level <= 10):
            return False
        if not (0 <= self.priority_score <= 100):
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "message_id": self.message_id,
            "summary": self.summary,
            "sentiment": self.sentiment.value,
            "sentiment_score": self.sentiment_score,
            "urgency_level": self.urgency_level,
            "priority_score": self.priority_score,
            "tone": self.tone.value,
            "extracted_tasks": [task.to_dict() for task in self.extracted_tasks],
            "requires_response": self.requires_response,
            "suggested_response_time": self.suggested_response_time,
            "metadata": self.metadata,
        }


@dataclass
class Task:
    """
    Represents an actionable task extracted from a message.
    """

    id: str
    title: str
    description: str
    source_message_id: str
    priority: int  # 0-100
    deadline: Optional[str] = None  # ISO format datetime string
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set defaults and convert enums"""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

        if isinstance(self.status, str):
            self.status = TaskStatus(self.status.lower())

    def validate(self) -> bool:
        """Validate task data"""
        if not self.id or not self.title or not self.source_message_id:
            return False
        if not (0 <= self.priority <= 100):
            return False
        return True

    def mark_completed(self) -> None:
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "source_message_id": self.source_message_id,
            "priority": self.priority,
            "deadline": self.deadline,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            source_message_id=data["source_message_id"],
            priority=data["priority"],
            deadline=data.get("deadline"),
            status=TaskStatus(data.get("status", "pending")),
            assigned_to=data.get("assigned_to"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Intent:
    """
    Represents user intent classification result.
    Used by orchestrator to route commands to appropriate agents.
    """

    action: str  # e.g., "send", "fetch", "summarize", "create_task"
    target: str  # e.g., "gmail", "slack", "system"
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0  # 0.0 to 1.0
    original_command: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate intent data"""
        if not self.action or not self.target:
            return False
        if not (0.0 <= self.confidence <= 1.0):
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "action": self.action,
            "target": self.target,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "original_command": self.original_command,
            "metadata": self.metadata,
        }


@dataclass
class Context:
    """
    Represents conversation context for LLM memory.
    Used to maintain context across interactions.
    """

    session_id: str
    user_input: str
    response: str
    timestamp: str
    intent: Optional[Intent] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "session_id": self.session_id,
            "user_input": self.user_input,
            "response": self.response,
            "timestamp": self.timestamp,
            "intent": self.intent.to_dict() if self.intent else None,
            "metadata": self.metadata,
        }


@dataclass
class Notification:
    """
    Represents a notification to be shown to the user.
    """

    id: str
    title: str
    message: str
    source: MessageSource
    priority: int  # 0-100
    timestamp: str
    action_url: Optional[str] = None
    is_read: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

        if isinstance(self.source, str):
            self.source = MessageSource(self.source.lower())

    def mark_read(self) -> None:
        """Mark notification as read"""
        self.is_read = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "source": self.source.value,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "action_url": self.action_url,
            "is_read": self.is_read,
            "metadata": self.metadata,
        }
