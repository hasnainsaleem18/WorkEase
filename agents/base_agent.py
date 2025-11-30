"""
Base Agent Protocol for AutoReturn

Defines the interface that all communication agents (Gmail, Slack, etc.) must implement.
Agents are responsible for:
- Authenticating with their respective services
- Fetching incoming messages
- Sending outgoing messages
- Publishing events to the event bus
"""

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class Message:
    """
    Universal message format across all platforms.
    Agents convert platform-specific messages to this format.
    """

    id: str
    source: str  # 'gmail' or 'slack'
    sender: str
    content: str
    subject: Optional[str] = None
    thread_id: Optional[str] = None
    channel_id: Optional[str] = None
    timestamp: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None  # Platform-specific data

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class Agent(Protocol):
    """
    Protocol defining the interface for all communication agents.

    Each agent (Gmail, Slack) must implement these methods to integrate
    with the WorkEase orchestrator.
    """

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the agent and authenticate with the service.

        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def fetch_messages(self, limit: int = 10) -> List[Message]:
        """
        Fetch new/unread messages from the service.

        Args:
            limit: Maximum number of messages to fetch

        Returns:
            List[Message]: List of messages in universal format
        """
        pass

    @abstractmethod
    async def send_message(
        self,
        recipient: str,
        content: str,
        subject: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> bool:
        """
        Send a message through this agent's service.

        Args:
            recipient: Recipient email/username
            content: Message content
            subject: Subject line (for email)
            thread_id: Thread/conversation ID for replies

        Returns:
            bool: True if send successful, False otherwise
        """
        pass

    @abstractmethod
    async def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read in the service.

        Args:
            message_id: ID of the message to mark as read

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_agent_name(self) -> str:
        """
        Get the name/type of this agent.

        Returns:
            str: Agent name ('gmail' or 'slack')
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Cleanup and shutdown the agent gracefully.
        Closes connections, saves state, etc.
        """
        pass


class BaseAgent:
    """
    Base implementation providing common functionality for all agents.
    Actual agents (GmailAgent, SlackAgent) should inherit from this.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.is_initialized = False

    async def get_agent_name(self) -> str:
        """Return the agent's name."""
        return self.agent_name

    def _validate_initialized(self) -> None:
        """
        Raise exception if agent is not initialized.
        Call this at the start of methods that require initialization.
        """
        if not self.is_initialized:
            raise RuntimeError(
                f"{self.agent_name} agent not initialized. Call initialize() first."
            )
