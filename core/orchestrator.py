"""
Orchestrator - Central Intent Router

The orchestrator receives user intents (from voice or UI), classifies them
using the local LLM, and routes them to the appropriate agent via the event bus.
"""

import logging
from dataclasses import dataclass
from typing import Any, Optional

from core.event_bus import EventBus

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Structured representation of a user intent."""

    action: str  # "fetch", "send", "create", "summarize", etc.
    target: str  # "gmail", "slack", "jira"
    parameters: dict[str, Any]
    confidence: float
    context_id: str
    raw_input: str


class Orchestrator:
    """
    Central orchestrator for intent classification and routing.

    The orchestrator acts as the brain of AUTOCOM, receiving user commands,
    understanding them via LLM, and dispatching them to the right agents.
    """

    def __init__(
        self,
        llm: Any,  # LocalLLM instance
        memory: Any,  # MemoryStore instance
        event_bus: EventBus,
        confidence_threshold: float = 0.7,
    ) -> None:
        """
        Initialize the orchestrator.

        Args:
            llm: Local LLM instance for intent classification
            memory: Memory store for context persistence
            event_bus: Event bus for agent communication
            confidence_threshold: Minimum confidence for intent execution
        """
        self.llm = llm
        self.memory = memory
        self.event_bus = event_bus
        self.confidence_threshold = confidence_threshold
        self.agent_registry: dict[str, Any] = {}

    async def register_agent(self, name: str, agent: Any) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            name: Agent identifier (e.g., "gmail", "slack")
            agent: Agent instance
        """
        self.agent_registry[name] = agent
        logger.info(f"Agent registered: {name}")

    async def process_intent(self, user_input: str, context_id: str = "default") -> None:
        """
        Main entry point for processing user intents.

        Args:
            user_input: Raw user command (text or transcribed speech)
            context_id: Session/conversation identifier
        """
        try:
            logger.info(f"Processing intent: {user_input}")

            # Get conversation context from memory
            context = await self.memory.get_recent_context(limit=10)

            # Classify intent using LLM
            intent = await self.classify_intent(user_input, context, context_id)

            # Check confidence threshold
            if intent.confidence < self.confidence_threshold:
                logger.warning(
                    f"Low confidence ({intent.confidence}), requesting clarification"
                )
                await self._request_clarification(user_input)
                return

            # Route to appropriate agent
            await self.route_to_agent(intent)

            # Store interaction in memory
            await self.memory.store_interaction(intent, "")

        except Exception as e:
            logger.error(f"Error processing intent: {e}", exc_info=True)
            await self.event_bus.emit(
                "orchestrator.error", {"error": str(e), "input": user_input}
            )

    async def classify_intent(
        self, user_input: str, context: list[dict[str, Any]], context_id: str
    ) -> Intent:
        """
        Classify user input into a structured intent using LLM.

        Args:
            user_input: Raw user command
            context: Recent conversation history
            context_id: Session identifier

        Returns:
            Structured Intent object
        """
        # Build context string from history
        context_str = "\n".join(
            [f"User: {item.get('user_input', '')}" for item in context[-5:]]
        )

        # Construct LLM prompt
        prompt = f"""You are AUTOCOM, an automation assistant. Analyze the user's command and extract:
1. Action (fetch, send, create, update, summarize, etc.)
2. Target service (gmail, slack, jira)
3. Parameters (recipients, content, filters, etc.)

Recent context:
{context_str}

Current command: {user_input}

Respond with JSON only:
{{
    "action": "action_name",
    "target": "service_name",
    "parameters": {{}},
    "confidence": 0.0-1.0
}}"""

        # Get LLM response
        response = await self.llm.classify_intent(prompt, context)

        # Parse response into Intent
        intent = Intent(
            action=response.get("action", "unknown"),
            target=response.get("target", "unknown"),
            parameters=response.get("parameters", {}),
            confidence=response.get("confidence", 0.0),
            context_id=context_id,
            raw_input=user_input,
        )

        logger.info(f"Intent classified: {intent}")
        return intent

    async def route_to_agent(self, intent: Intent) -> None:
        """
        Route an intent to the appropriate agent via event bus.

        Args:
            intent: Classified intent to route
        """
        if intent.target not in self.agent_registry:
            logger.error(f"No agent registered for target: {intent.target}")
            await self.event_bus.emit(
                "orchestrator.error",
                {"error": f"Unknown target: {intent.target}", "intent": intent},
            )
            return

        # Emit intent event for the target agent
        event_name = f"agent.{intent.target}.{intent.action}"
        await self.event_bus.emit(
            event_name,
            {
                "intent": intent,
                "action": intent.action,
                "parameters": intent.parameters,
            },
        )

        logger.info(f"Intent routed to {intent.target}: {intent.action}")

    async def handle_agent_response(self, response: dict[str, Any]) -> None:
        """
        Handle responses from agents.

        Args:
            response: Agent response data
        """
        try:
            if response.get("success"):
                logger.info(f"Agent response successful: {response.get('agent_name')}")
                # Emit to UI for display
                await self.event_bus.emit("ui.update", response)
                # Emit to voice for TTS feedback
                await self.event_bus.emit("voice.speak", response)
            else:
                logger.error(f"Agent response failed: {response.get('error')}")
                await self.event_bus.emit("ui.error", response)

        except Exception as e:
            logger.error(f"Error handling agent response: {e}", exc_info=True)

    async def _request_clarification(self, user_input: str) -> None:
        """
        Request clarification from user when intent is ambiguous.

        Args:
            user_input: Original user input
        """
        clarification_message = (
            f"I'm not sure I understood. Could you rephrase: '{user_input}'?"
        )
        await self.event_bus.emit(
            "voice.speak", {"text": clarification_message, "priority": "high"}
        )
        await self.event_bus.emit(
            "ui.notification",
            {"title": "Clarification Needed", "body": clarification_message},
        )
