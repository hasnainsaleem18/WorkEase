"""
WorkEase Memory Package

This package provides context and memory management for the WorkEase orchestrator.
It implements different memory providers that follow the ContextProvider protocol:

- Simple SQLite memory store (lightweight, default)
- LangChain memory (enhanced context retention)
- RAG vector store (semantic search across history)

The appropriate provider can be selected through configuration, allowing
the orchestrator to maintain conversation history and context across interactions.
"""

from core.memory.context_provider import ContextProvider
from core.memory.langchain_memory import LangChainMemoryProvider
from core.memory.rag_provider import ChromaRAGProvider, RAGProvider

# Re-export components for easier imports
__all__ = [
    "ContextProvider",
    "LangChainMemoryProvider",
    "RAGProvider",
    "ChromaRAGProvider",
]
