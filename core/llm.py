"""
Local LLM Integration using Ollama

Handles all LLM inference for intent classification, task extraction,
and natural language understanding.
"""

import json
import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class LocalLLM:
    """
    Local LLM interface using Ollama.

    Provides structured output for intent classification and
    natural language understanding tasks.
    """

    def __init__(
        self,
        model: str = "llama3.1:8b",
        endpoint: str = "http://localhost:11434",
        temperature: float = 0.3,
        max_tokens: int = 500,
    ) -> None:
        """
        Initialize the LLM client.

        Args:
            model: Ollama model name
            endpoint: Ollama API endpoint
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens in response
        """
        self.model = model
        self.endpoint = endpoint
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = httpx.AsyncClient(timeout=30.0)

    async def generate(
        self, prompt: str, system: str = "", temperature: Optional[float] = None
    ) -> str:
        """
        Generate text completion from the LLM.

        Args:
            prompt: User prompt
            system: System prompt for context
            temperature: Override default temperature

        Returns:
            Generated text response
        """
        try:
            response = await self.client.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "temperature": temperature or self.temperature,
                    "max_tokens": self.max_tokens,
                    "stream": False,
                },
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")

        except httpx.HTTPError as e:
            logger.error(f"LLM request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in LLM generation: {e}")
            raise

    async def classify_intent(
        self, prompt: str, context: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Classify user intent into structured format.

        Args:
            prompt: Formatted prompt with user input
            context: Recent conversation history

        Returns:
            Dictionary with action, target, parameters, confidence
        """
        system_prompt = """You are an intent classifier for AUTOCOM automation system.
Extract structured information from user commands.
Always respond with valid JSON only, no additional text.
Format: {"action": "...", "target": "...", "parameters": {...}, "confidence": 0.0-1.0}

Available targets: gmail, slack, jira
Common actions: fetch, send, create, update, summarize, archive, mark_read"""

        try:
            response_text = await self.generate(prompt, system=system_prompt)

            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                logger.warning("No JSON found in LLM response, using fallback")
                return self._fallback_parse(prompt)

            json_str = response_text[json_start:json_end]
            intent_data = json.loads(json_str)

            # Validate required fields
            required_fields = ["action", "target", "parameters", "confidence"]
            if not all(field in intent_data for field in required_fields):
                logger.warning("Incomplete intent data, using fallback")
                return self._fallback_parse(prompt)

            return intent_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            return self._fallback_parse(prompt)
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            return self._fallback_parse(prompt)

    async def extract_task(self, message: str) -> Optional[dict[str, Any]]:
        """
        Extract actionable task from a message.

        Args:
            message: Message text to analyze

        Returns:
            Task dictionary or None if no task found
        """
        prompt = f"""Analyze this message and extract any actionable task.
If there's a task, respond with JSON: {{"title": "...", "description": "...", "priority": "low|normal|high"}}
If no task, respond with: {{"task": false}}

Message: {message}"""

        try:
            response_text = await self.generate(prompt)
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1:
                return None

            json_str = response_text[json_start:json_end]
            task_data = json.loads(json_str)

            if task_data.get("task") is False:
                return None

            return task_data

        except Exception as e:
            logger.error(f"Error extracting task: {e}")
            return None

    def _fallback_parse(self, prompt: str) -> dict[str, Any]:
        """
        Rule-based fallback when LLM fails.

        Args:
            prompt: Original user input

        Returns:
            Best-guess intent dictionary
        """
        prompt_lower = prompt.lower()

        # Simple keyword matching
        if "email" in prompt_lower or "gmail" in prompt_lower:
            target = "gmail"
        elif "slack" in prompt_lower or "message" in prompt_lower:
            target = "slack"
        elif "jira" in prompt_lower or "ticket" in prompt_lower or "task" in prompt_lower:
            target = "jira"
        else:
            target = "unknown"

        if "send" in prompt_lower or "write" in prompt_lower:
            action = "send"
        elif "read" in prompt_lower or "check" in prompt_lower or "show" in prompt_lower:
            action = "fetch"
        elif "create" in prompt_lower or "new" in prompt_lower:
            action = "create"
        else:
            action = "unknown"

        return {
            "action": action,
            "target": target,
            "parameters": {},
            "confidence": 0.5,  # Low confidence for fallback
        }

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
