"""
Sentiment Analyzer - Message Tone and Urgency Detection

Analyzes messages to detect emotional tone and urgency level
for intelligent notification prioritization.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result."""

    message_id: str
    tone: str  # "positive", "neutral", "negative", "urgent"
    urgency_score: float  # 0-10
    confidence: float
    keywords: list[str]
    analyzed_at: datetime


class SentimentAnalyzer:
    """
    Analyzes message sentiment and urgency.

    Uses both LLM-based analysis and rule-based pattern matching
    for reliable sentiment detection and urgency scoring.
    """

    # Urgency pattern keywords with scores
    URGENCY_PATTERNS = {
        r"\burgent\b": 10,
        r"\basap\b": 10,
        r"\bimmediately\b": 10,
        r"\bcritical\b": 9,
        r"\bemergency\b": 9,
        r"\bimportant\b": 8,
        r"\bpriority\b": 7,
        r"\btoday\b": 7,
        r"\bnow\b": 7,
        r"\bsoon\b": 6,
        r"\btomorrow\b": 5,
        r"\bthis week\b": 4,
    }

    # Negative sentiment patterns
    NEGATIVE_PATTERNS = [
        r"\bproblem\b",
        r"\bissue\b",
        r"\berror\b",
        r"\bfailed\b",
        r"\bbroken\b",
        r"\bwrong\b",
        r"\bbug\b",
        r"\bcrash\b",
        r"\bdown\b",
        r"\bnot working\b",
    ]

    # Positive sentiment patterns
    POSITIVE_PATTERNS = [
        r"\bthanks\b",
        r"\bthank you\b",
        r"\bgreat\b",
        r"\bexcellent\b",
        r"\bawesome\b",
        r"\bperfect\b",
        r"\bgood job\b",
        r"\bwell done\b",
        r"\bappreciate\b",
    ]

    def __init__(self, llm: Any) -> None:
        """
        Initialize the sentiment analyzer.

        Args:
            llm: Local LLM instance for advanced analysis
        """
        self.llm = llm
        self.analysis_cache: dict[str, SentimentAnalysis] = {}

    async def analyze_message(
        self, message: dict[str, Any], sender_priority: bool = False
    ) -> SentimentAnalysis:
        """
        Analyze message sentiment and urgency.

        Args:
            message: Message data with id, text, sender
            sender_priority: Whether sender is marked as priority

        Returns:
            SentimentAnalysis result
        """
        message_id = message.get("id", "")
        text = message.get("text", "") or message.get("body", "")
        sender = message.get("sender", "") or message.get("from", "")

        # Check cache
        if message_id in self.analysis_cache:
            return self.analysis_cache[message_id]

        try:
            # Calculate urgency score
            urgency_score = self._calculate_urgency_score(text, sender_priority)

            # Detect tone
            tone = self._detect_tone(text, urgency_score)

            # Extract keywords
            keywords = self._extract_keywords(text)

            # Create analysis result
            analysis = SentimentAnalysis(
                message_id=message_id,
                tone=tone,
                urgency_score=urgency_score,
                confidence=0.85,  # Rule-based confidence
                keywords=keywords,
                analyzed_at=datetime.now(),
            )

            # Cache result
            self.analysis_cache[message_id] = analysis

            logger.debug(
                f"Sentiment analyzed: {message_id} - {tone} (urgency: {urgency_score})"
            )
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}", exc_info=True)
            # Return neutral default
            return SentimentAnalysis(
                message_id=message_id,
                tone="neutral",
                urgency_score=5.0,
                confidence=0.5,
                keywords=[],
                analyzed_at=datetime.now(),
            )

    def _calculate_urgency_score(self, text: str, sender_priority: bool) -> float:
        """
        Calculate urgency score based on text patterns.

        Args:
            text: Message text
            sender_priority: Whether sender is priority

        Returns:
            Urgency score (0-10)
        """
        text_lower = text.lower()
        max_score = 0.0

        # Check urgency patterns
        for pattern, score in self.URGENCY_PATTERNS.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                max_score = max(max_score, score)

        # Boost score for priority senders
        if sender_priority and max_score > 0:
            max_score = min(10.0, max_score + 1.0)

        # Check for multiple exclamation marks (urgency indicator)
        exclamation_count = text.count("!")
        if exclamation_count >= 2:
            max_score = max(max_score, 6.0)

        # Check for all caps (urgency indicator)
        if text.isupper() and len(text) > 10:
            max_score = max(max_score, 7.0)

        return max_score

    def _detect_tone(self, text: str, urgency_score: float) -> str:
        """
        Detect emotional tone of message.

        Args:
            text: Message text
            urgency_score: Calculated urgency score

        Returns:
            Tone classification
        """
        text_lower = text.lower()

        # Urgent takes precedence
        if urgency_score >= 8:
            return "urgent"

        # Check negative patterns
        negative_count = sum(
            1 for pattern in self.NEGATIVE_PATTERNS if re.search(pattern, text_lower)
        )

        # Check positive patterns
        positive_count = sum(
            1 for pattern in self.POSITIVE_PATTERNS if re.search(pattern, text_lower)
        )

        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"

    def _extract_keywords(self, text: str) -> list[str]:
        """
        Extract important keywords from text.

        Args:
            text: Message text

        Returns:
            List of keywords
        """
        keywords = []
        text_lower = text.lower()

        # Extract urgency keywords
        for pattern in self.URGENCY_PATTERNS.keys():
            match = re.search(pattern, text_lower)
            if match:
                keywords.append(match.group())

        # Extract negative keywords
        for pattern in self.NEGATIVE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                keywords.append(match.group())

        # Extract positive keywords
        for pattern in self.POSITIVE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                keywords.append(match.group())

        return list(set(keywords))[:5]  # Return top 5 unique keywords

    def get_priority_from_sentiment(self, analysis: SentimentAnalysis) -> str:
        """
        Convert sentiment analysis to notification priority.

        Args:
            analysis: Sentiment analysis result

        Returns:
            Priority level ("low", "normal", "high", "urgent")
        """
        if analysis.urgency_score >= 9:
            return "urgent"
        elif analysis.urgency_score >= 7:
            return "high"
        elif analysis.urgency_score >= 4:
            return "normal"
        else:
            return "low"

    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self.analysis_cache.clear()
        logger.info("Sentiment analysis cache cleared")

    def get_stats(self) -> dict[str, Any]:
        """
        Get sentiment analyzer statistics.

        Returns:
            Dictionary with stats
        """
        tone_counts = {}
        for analysis in self.analysis_cache.values():
            tone_counts[analysis.tone] = tone_counts.get(analysis.tone, 0) + 1

        avg_urgency = (
            sum(a.urgency_score for a in self.analysis_cache.values())
            / len(self.analysis_cache)
            if self.analysis_cache
            else 0
        )

        return {
            "cached_analyses": len(self.analysis_cache),
            "tone_distribution": tone_counts,
            "average_urgency": round(avg_urgency, 2),
        }
