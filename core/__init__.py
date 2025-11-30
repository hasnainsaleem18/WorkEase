"""
WorkEase Core Package

Contains the central orchestrator, LLM clients, and data models.
"""

from core.llm_client import LLMClient, MockLLMClient, OllamaLLMClient
from core.models import (
    Context,
    Intent,
    Message,
    MessageAnalysis,
    MessageSource,
    Notification,
    SentimentType,
    Task,
    TaskStatus,
    ToneType,
)
from core.orchestrator import MessageSummary, Orchestrator

__all__ = [
    # LLM Clients
    "LLMClient",
    "OllamaLLMClient",
    "MockLLMClient",
    # Orchestrator
    "Orchestrator",
    "MessageSummary",
    # Models
    "Message",
    "MessageSource",
    "MessageAnalysis",
    "Task",
    "TaskStatus",
    "Intent",
    "Context",
    "Notification",
    "SentimentType",
    "ToneType",
]
