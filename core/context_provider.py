"""
Context Provider Protocol - Abstraction for Memory/Context Systems

This module defines the interface that any context provider must implement.
This allows swapping between simple SQLite storage, LangChain memory,
or RAG systems without changing the orchestrator code.

Future implementations:
- SimpleMemoryStore (current SQLite implementation)
- LangChainMemoryProvider (LangChain integration)
- RAGContextProvider (RAG with vector databases)
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol

import numpy as np


class ContextProvider(Protocol):
    """
    Protocol defining the interface for context/memory providers.

    Any class implementing this protocol can be used by the orchestrator
    for context management, whether it's simple SQLite, LangChain, or RAG.
    """

    async def initialize(self) -> None:
        """Initialize the context provider (connect to DB, load models, etc.)"""
        ...

    async def store_interaction(
        self,
        intent: Any,
        response: str,
        embedding: Optional[np.ndarray] = None,
    ) -> None:
        """
        Store a user interaction.

        Args:
            intent: Intent object from orchestrator
            response: Agent response text
            embedding: Optional vector embedding for semantic search
        """
        ...

    async def get_recent_context(
        self, limit: int = 10, context_id: str = "default"
    ) -> list[dict[str, Any]]:
        """
        Retrieve recent conversation history.

        Args:
            limit: Maximum number of interactions to retrieve
            context_id: Session identifier

        Returns:
            List of recent interactions with user_input, intent, response
        """
        ...

    async def search_similar(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> list[dict[str, Any]]:
        """
        Search for similar past interactions (semantic search).

        Args:
            query_embedding: Query vector
            k: Number of results to return

        Returns:
            List of similar interactions with similarity scores
        """
        ...

    async def clear_session(self, session_id: str) -> None:
        """
        Clear conversation history for a session.

        Args:
            session_id: Session identifier to clear
        """
        ...

    async def close(self) -> None:
        """Close connections and cleanup resources."""
        ...


class BaseContextProvider(ABC):
    """
    Abstract base class for context providers.

    Use this if you prefer inheritance over Protocol.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the context provider."""
        pass

    @abstractmethod
    async def store_interaction(
        self,
        intent: Any,
        response: str,
        embedding: Optional[np.ndarray] = None,
    ) -> None:
        """Store a user interaction."""
        pass

    @abstractmethod
    async def get_recent_context(
        self, limit: int = 10, context_id: str = "default"
    ) -> list[dict[str, Any]]:
        """Retrieve recent conversation history."""
        pass

    @abstractmethod
    async def search_similar(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> list[dict[str, Any]]:
        """Search for similar past interactions."""
        pass

    @abstractmethod
    async def clear_session(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close connections and cleanup."""
        pass


# Future implementation examples (not implemented yet):

# class LangChainMemoryProvider(BaseContextProvider):
#     """
#     LangChain-based memory provider.
#
#     Uses LangChain's ConversationBufferMemory or ConversationSummaryMemory
#     for more sophisticated context management.
#     """
#     def __init__(self, llm, memory_type: str = "buffer"):
#         from langchain.memory import ConversationBufferMemory
#         self.memory = ConversationBufferMemory()
#         # Implementation here...


# class RAGContextProvider(BaseContextProvider):
#     """
#     RAG-based context provider.
#
#     Uses vector databases (Chroma, Pinecone, Weaviate) for
#     retrieval-augmented generation with large document collections.
#     """
#     def __init__(self, vector_db_url: str, embedding_model: str):
#         from langchain.vectorstores import Chroma
#         self.vector_store = Chroma(...)
#         # Implementation here...
