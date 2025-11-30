"""
LLM Client Module for AutoReturn

Provides interface to Local LLM (Ollama) or Cloud LLM APIs.
The LLM serves as the central brain for decision-making, analysis, and generation.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import aiohttp


@dataclass
class Intent:
    """Represents parsed user intent."""

    action: str  # 'send', 'fetch', 'create', 'delete', 'update', 'summarize'
    target: str  # 'gmail', 'slack', 'task', 'notification'
    parameters: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    raw_command: str


@dataclass
class MessageAnalysis:
    """Represents LLM analysis of a message."""

    sentiment: float  # -1.0 (negative) to 1.0 (positive)
    urgency: int  # 0-10 scale
    priority: int  # 0-100 scale
    tone: str  # 'URGENT', 'NEGATIVE', 'POSITIVE', 'NEUTRAL'
    summary: str  # AI-generated summary
    tasks: List[str]  # Extracted action items
    requires_response: bool


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    Allows swapping between local Ollama, OpenAI, Anthropic, etc.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the LLM client and verify connection."""
        pass

    @abstractmethod
    async def understand_intent(
        self, user_input: str, context: Optional[List[Dict]] = None
    ) -> Intent:
        """
        Analyze user command and determine intent.

        Args:
            user_input: The user's natural language command
            context: Recent conversation context for better understanding

        Returns:
            Intent object with action, target, parameters, and confidence
        """
        pass

    @abstractmethod
    async def analyze_message(
        self, message_content: str, sender: str, subject: str = ""
    ) -> MessageAnalysis:
        """
        Analyze incoming message for sentiment, urgency, priority, and tasks.

        Args:
            message_content: The message body
            sender: Who sent the message
            subject: Email subject line (if applicable)

        Returns:
            MessageAnalysis with all extracted insights
        """
        pass

    @abstractmethod
    async def generate_summary(
        self, message_content: str, source: str, sender: str
    ) -> str:
        """
        Generate a concise AI summary of a message.

        Args:
            message_content: The full message text
            source: 'gmail' or 'slack'
            sender: Message sender

        Returns:
            Concise summary string
        """
        pass

    @abstractmethod
    async def extract_tasks(self, text: str) -> List[str]:
        """
        Extract actionable tasks from text.

        Args:
            text: The text to analyze (could be message or summary)

        Returns:
            List of task strings
        """
        pass

    @abstractmethod
    async def generate_draft(self, original_message: str, context: str = "") -> str:
        """
        Generate appropriate reply draft.

        Args:
            original_message: The message to reply to
            context: Additional context about the conversation

        Returns:
            Draft reply text
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""
        pass


class OllamaLLMClient(LLMClient):
    """
    Local LLM client using Ollama.
    Privacy-first: All processing happens on-device.
    """

    def __init__(
        self,
        model: str = "llama3.2:3b",
        base_url: str = "http://localhost:11434",
        timeout: int = 30,
    ):
        """
        Initialize Ollama client.

        Args:
            model: Ollama model name (e.g., 'llama3.2:3b', 'llama3.1:8b')
            base_url: Ollama API endpoint
            timeout: Request timeout in seconds
        """
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self) -> None:
        """Initialize HTTP session and verify Ollama is running."""
        self.session = aiohttp.ClientSession()
        try:
            # Test connection
            async with self.session.get(f"{self.base_url}/api/tags", timeout=5) as resp:
                if resp.status != 200:
                    raise ConnectionError(f"Ollama not responding: {resp.status}")
                models = await resp.json()
                # Check if our model is available
                model_names = [m["name"] for m in models.get("models", [])]
                if self.model not in model_names:
                    print(
                        f"Warning: Model '{self.model}' not found. Available: {model_names}"
                    )
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to Ollama at {self.base_url}: {e}"
            )

    async def _generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Internal method to generate completion from Ollama.

        Args:
            prompt: The prompt to send
            system_prompt: System instructions for the LLM

        Returns:
            Generated text response
        """
        if not self.session:
            raise RuntimeError("LLM client not initialized. Call initialize() first.")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(
                        f"Ollama API error: {resp.status} - {error_text}"
                    )

                result = await resp.json()
                return result.get("response", "").strip()
        except asyncio.TimeoutError:
            raise TimeoutError(f"LLM request timed out after {self.timeout}s")

    async def understand_intent(
        self, user_input: str, context: Optional[List[Dict]] = None
    ) -> Intent:
        """Analyze user command and determine intent using LLM."""
        context_str = ""
        if context:
            context_str = "\nRecent context:\n" + "\n".join(
                [f"- {c.get('summary', '')}" for c in context[:3]]
            )

        You are the brain of AutoReturn, a communication automation assistant.
Analyze this user command and determine:
- Action: what they want to do (send, fetch, create, delete, update, summarize, search)
- Target: which service (gmail, slack, task, notification)
- Parameters: extract recipients, subject, content, filters, etc.
- Confidence: how certain you are (0.0 to 1.0)

User command: "{user_input}"{context_str}

Respond in valid JSON format only:
{{"action": "...", "target": "...", "parameters": {{}}, "confidence": 0.95}}"""

        response = await self._generate(prompt)

        # Parse JSON response
        try:
            # Extract JSON from response (sometimes LLM adds extra text)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return Intent(
                    action=data.get("action", "unknown"),
                    target=data.get("target", "unknown"),
                    parameters=data.get("parameters", {}),
                    confidence=float(data.get("confidence", 0.5)),
                    raw_command=user_input,
                )
        except json.JSONDecodeError:
            pass

        # Fallback to low-confidence unknown intent
        return Intent(
            action="unknown",
            target="unknown",
            parameters={},
            confidence=0.1,
            raw_command=user_input,
        )

    async def analyze_message(
        self, message_content: str, sender: str, subject: str = ""
    ) -> MessageAnalysis:
        """Analyze incoming message using LLM."""
        prompt = f"""Analyze this message and provide insights:
- Sentiment: positive/negative/neutral (-1.0 to 1.0)
- Urgency: how urgent (0-10 scale)
- Priority: overall priority (0-100)
- Tone: URGENT/NEGATIVE/POSITIVE/NEUTRAL
- Summary: One concise sentence summarizing the key point
- Tasks: Any action items found (as array)
- Requires Response: true/false if sender expects a reply

Sender: {sender}
Subject: {subject}
Message: "{message_content}"

Respond in valid JSON format only:
{{"sentiment": 0.5, "urgency": 5, "priority": 50, "tone": "NEUTRAL", "summary": "...", "tasks": [], "requires_response": false}}"""

        response = await self._generate(prompt)

        # Parse JSON response
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return MessageAnalysis(
                    sentiment=float(data.get("sentiment", 0.0)),
                    urgency=int(data.get("urgency", 5)),
                    priority=int(data.get("priority", 50)),
                    tone=data.get("tone", "NEUTRAL"),
                    summary=data.get("summary", "Message received"),
                    tasks=data.get("tasks", []),
                    requires_response=bool(data.get("requires_response", False)),
                )
        except (json.JSONDecodeError, ValueError, KeyError):
            pass

        # Fallback to neutral analysis
        return MessageAnalysis(
            sentiment=0.0,
            urgency=5,
            priority=50,
            tone="NEUTRAL",
            summary="Message analysis unavailable",
            tasks=[],
            requires_response=False,
        )

    async def generate_summary(
        self, message_content: str, source: str, sender: str
    ) -> str:
        """Generate concise AI summary of a message."""
        prompt = f"""You are an intelligent assistant for WorkEase.
Summarize this {source} message in ONE concise sentence. Capture the key point, sender intent, and any urgency:

Sender: {sender}
Content: {message_content}

Summary:"""

        summary = await self._generate(prompt)
        # Ensure it's one sentence, take first sentence if multiple
        return (
            summary.split(".")[0].strip() + "." if summary else "No summary available."
        )

    async def extract_tasks(self, text: str) -> List[str]:
        """Extract actionable tasks from text using LLM."""
        prompt = f"""You are the WorkEase task extraction assistant.
From this text, extract ALL actionable tasks as a bullet list.
Only include clear, specific tasks. Ignore non-actionable information.

Text: {text}

Tasks (bullet list):"""

        response = await self._generate(prompt)

        # Parse bullet list
        tasks = []
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("•") or line.startswith("*"):
                task = line.lstrip("-•* ").strip()
                if task:
                    tasks.append(task)

        return tasks if tasks else []

    async def generate_draft(self, original_message: str, context: str = "") -> str:
        """Generate appropriate reply draft using LLM."""
        context_note = f"\nContext: {context}" if context else ""

        prompt = f"""Generate an appropriate reply to this message.
Match the tone of the original sender.
Address all key points mentioned.
Keep it concise and professional.{context_note}

Original message: "{original_message}"

Generate reply:"""

        draft = await self._generate(prompt)
        return draft if draft else "Thank you for your message."

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()


class MockLLMClient(LLMClient):
    """
    Mock LLM for testing and development.
    Returns simple keyword-based responses.
    """

    async def initialize(self) -> None:
        """No initialization needed for mock."""
        pass

    async def understand_intent(
        self, user_input: str, context: Optional[List[Dict]] = None
    ) -> Intent:
        """Simple keyword-based intent parsing."""
        lower = user_input.lower()

        if "send" in lower or "email" in lower:
            return Intent("send", "gmail", {"content": user_input}, 0.8, user_input)
        elif "fetch" in lower or "get" in lower or "show" in lower:
            return Intent("fetch", "gmail", {}, 0.8, user_input)
        elif "slack" in lower:
            return Intent("send", "slack", {"content": user_input}, 0.7, user_input)
        else:
            return Intent("unknown", "unknown", {}, 0.3, user_input)

    async def analyze_message(
        self, message_content: str, sender: str, subject: str = ""
    ) -> MessageAnalysis:
        """Simple keyword-based analysis."""
        lower = message_content.lower()

        urgency = (
            7 if any(word in lower for word in ["urgent", "asap", "immediately"]) else 5
        )
        sentiment = 0.5 if any(word in lower for word in ["please", "thank"]) else 0.0
        tasks = (
            ["Complete task"]
            if any(word in lower for word in ["please", "need", "must"])
            else []
        )

        return MessageAnalysis(
            sentiment=sentiment,
            urgency=urgency,
            priority=urgency * 10,
            tone="URGENT" if urgency > 6 else "NEUTRAL",
            summary=f"Message from {sender}",
            tasks=tasks,
            requires_response=True,
        )

    async def generate_summary(
        self, message_content: str, source: str, sender: str
    ) -> str:
        """Simple summary."""
        return f"{sender} sent a {source} message about: {message_content[:50]}..."

    async def extract_tasks(self, text: str) -> List[str]:
        """Simple keyword task extraction."""
        tasks = []
        if "report" in text.lower():
            tasks.append("Prepare report")
        if "meeting" in text.lower():
            tasks.append("Attend meeting")
        if "update" in text.lower():
            tasks.append("Update system")
        return tasks

    async def generate_draft(self, original_message: str, context: str = "") -> str:
        """Simple draft generation."""
        return f"Thank you for your message. I'll address your points shortly."

    async def close(self) -> None:
        """No cleanup needed."""
        pass
