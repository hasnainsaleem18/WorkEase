"""
Base Agent Abstract Class

All service-specific agents must inherit from this class and implement
the required abstract methods.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential


class AgentConfig(BaseModel):
    """Configuration model for agents."""

    name: str
    enabled: bool = True
    endpoint: str = ""
    timeout: int = 10
    retry_attempts: int = 3


class AgentResponse(BaseModel):
    """Standardized response from agent operations."""

    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_name: str = ""


class AgentError(Exception):
    """Base exception for agent errors."""

    pass


class AuthenticationError(AgentError):
    """OAuth or token authentication failed."""

    pass


class RateLimitError(AgentError):
    """API rate limit exceeded."""

    pass


class NetworkError(AgentError):
    """Network connectivity issue."""

    pass


class BaseAgent(ABC):
    """
    Abstract base class for all FORGE agents.

    Each agent represents an integration with an external service
    (Gmail, Slack, Jira, etc.) and must implement authentication,
    data fetching, and action execution.
    """

    def __init__(self, config: AgentConfig) -> None:
        """
        Initialize the agent with configuration.

        Args:
            config: Agent configuration including credentials and settings
        """
        self.config = config
        self.authenticated = False
        self.client: Any = None

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Perform authentication with the external service.

        This method should handle OAuth2 flows, API token validation,
        or any other authentication mechanism required by the service.

        Returns:
            True if authentication successful, False otherwise

        Raises:
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    async def fetch(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Retrieve data from the external service.

        Args:
            params: Query parameters for filtering/pagination

        Returns:
            List of data items from the service

        Raises:
            NetworkError: If network request fails
            RateLimitError: If rate limit is exceeded
        """
        pass

    @abstractmethod
    async def act(self, action: str, data: dict[str, Any]) -> bool:
        """
        Execute an action on the external service.

        Args:
            action: Action type (e.g., "send", "create", "update")
            data: Action payload

        Returns:
            True if action successful, False otherwise

        Raises:
            NetworkError: If network request fails
            RateLimitError: If rate limit is exceeded
        """
        pass

    async def handle_intent(
        self, action: str, params: dict[str, Any]
    ) -> AgentResponse:
        """
        Main entry point for handling intents from the orchestrator.

        Args:
            action: Action type ("fetch" or specific action)
            params: Action parameters

        Returns:
            AgentResponse with success status and data/error
        """
        try:
            if not self.authenticated:
                auth_success = await self.authenticate()
                if not auth_success:
                    return AgentResponse(
                        success=False,
                        error="Authentication failed",
                        agent_name=self.config.name,
                    )

            if action == "fetch":
                results = await self.fetch(params)
                return AgentResponse(
                    success=True,
                    data={"results": results, "count": len(results)},
                    agent_name=self.config.name,
                )
            else:
                success = await self.act(action, params)
                return AgentResponse(
                    success=success,
                    data={"action": action},
                    agent_name=self.config.name,
                )

        except AuthenticationError as e:
            return AgentResponse(
                success=False, error=f"Authentication error: {str(e)}", agent_name=self.config.name
            )
        except RateLimitError as e:
            return AgentResponse(
                success=False, error=f"Rate limit exceeded: {str(e)}", agent_name=self.config.name
            )
        except NetworkError as e:
            return AgentResponse(
                success=False, error=f"Network error: {str(e)}", agent_name=self.config.name
            )
        except Exception as e:
            return AgentResponse(
                success=False, error=f"Unexpected error: {str(e)}", agent_name=self.config.name
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _retry_request(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Wrapper for retrying network requests with exponential backoff.

        Args:
            func: Async function to retry
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            Exception: If all retry attempts fail
        """
        return await func(*args, **kwargs)

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"<{self.__class__.__name__}(name={self.config.name}, enabled={self.config.enabled})>"
