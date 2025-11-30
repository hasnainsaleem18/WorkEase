"""
Context Provider Interface for AutoReturn

Defines the protocol that all context/memory providers must implement.
This allows the orchestrator to work with different memory implementations:
- Simple SQLite memory store (default, lightweight)
- LangChain memory (enhanced context retention)
- RAG vector store (semantic search across history)

The Context Provider is a critical component that enables the orchestrator
to maintain conversation history and context across interactions.
"""

from typing import Any, Dict, List, Optional, Protocol


class ContextProvider(Protocol):
    """
    Protocol defining the interface for any context/memory provider.

    All context providers must implement these methods to be compatible
    with the WorkEase orchestrator. This allows easy swapping between
    different implementations (SQLite, LangChain, RAG) without changing
    the orchestrator code.
    """

    async def initialize(self) -> None:
        """
        Initialize the context provider and prepare storage.

        This method should establish connections, create tables/collections,
        and perform any setup required before the provider can be used.
        """
        ...

    async def store_interaction(
        self,
        intent: Dict[str, Any],
        response: str,
        embedding: Optional[List[float]] = None,
    ) -> None:
        """
        Store an interaction with embedding for future context.

        Args:
            intent: The user intent/input with at least action and text
            response: The system's response to the user
            embedding: Optional pre-computed embedding vector (for RAG providers)
        """
        ...

    async def get_recent_context(
        self, limit: int = 10, context_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get most recent context entries.

        Args:
            limit: Maximum number of entries to retrieve
            context_id: Optional session/conversation ID to filter by

        Returns:
            List of context entries, most recent first. Each entry should
            have at least 'content', 'role', and 'timestamp' fields.
        """
        ...

    async def search_similar(
        self, query_embedding: List[float], k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for contexts similar to the provided embedding.

        This method is primarily used by RAG providers for semantic search.
        Simple providers may return recent contexts instead.

        Args:
            query_embedding: Vector embedding to search for
            k: Number of results to return

        Returns:
            List of similar context entries with similarity scores
        """
        ...

    async def clear_session(self, session_id: str) -> None:
        """
        Clear context for a specific session.

        Args:
            session_id: Session ID to clear
        """
        ...

    async def close(self) -> None:
        """
        Close connections and clean up resources.

        This should be called when the provider is no longer needed
        to ensure proper cleanup of database connections, file handles, etc.
        """
        ...
