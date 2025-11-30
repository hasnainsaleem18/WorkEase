"""
Algorithms Package for WorkEase

Contains custom algorithm implementations for:
- Task extraction
- Priority scoring
- Sentiment analysis
- Intent classification
- Context matching
"""

from .task_extractor import ExtractedTask, TaskExtractor, TaskPriority

__all__ = [
    "TaskExtractor",
    "ExtractedTask",
    "TaskPriority",
]
