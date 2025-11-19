"""
Memory Store - Context and Conversation Persistence

Handles storage of conversation history, context, and vector embeddings
for semantic search using SQLite.

This is the default simple implementation of ContextProvider.
For LangChain or RAG integration, see core/context_provider.py
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import aiosqlite
import numpy as np

logger = logging.getLogger(__name__)


class MemoryStore:
    """
    Persistent memory store for conversation context and history.

    Uses SQLite for structured data and BLOB storage for vector embeddings.
    """

    def __init__(self, db_path: str = "memory/context.db") -> None:
        """
        Initialize the memory store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        """Create database tables if they don't exist."""
        self.connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        logger.info(f"Memory store initialized at {self.db_path}")

    async def _create_tables(self) -> None:
        """Create database schema."""
        if not self.connection:
            raise RuntimeError("Database connection not initialized")

        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                user_input TEXT NOT NULL,
                intent_json TEXT NOT NULL,
                agent_response TEXT,
                embedding BLOB,
                context_id TEXT NOT NULL
            )
            """
        )

        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS context (
                session_id TEXT PRIMARY KEY,
                last_active DATETIME NOT NULL,
                context_json TEXT NOT NULL
            )
            """
        )

        await self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        # Create indexes for performance
        await self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)"
        )
        await self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_context_id ON conversations(context_id)"
        )

        await self.connection.commit()

    async def store_interaction(
        self,
        intent: Any,  # Intent object
        response: str,
        embedding: Optional[np.ndarray] = None,
    ) -> None:
        """
        Store a user interaction in the database.

        Args:
            intent: Intent object from orchestrator
            response: Agent response text
            embedding: Optional vector embedding for semantic search
        """
        if not self.connection:
            raise RuntimeError("Database connection not initialized")

        intent_json = json.dumps(
            {
                "action": intent.action,
                "target": intent.target,
                "parameters": intent.parameters,
                "confidence": intent.confidence,
            }
        )

        embedding_blob = (
            embedding.tobytes() if embedding is not None else None
        )

        await self.connection.execute(
            """
            INSERT INTO conversations 
            (timestamp, user_input, intent_json, agent_response, embedding, context_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(),
                intent.raw_input,
                intent_json,
                response,
                embedding_blob,
                intent.context_id,
            ),
        )
        await self.connection.commit()
        logger.debug(f"Interaction stored: {intent.raw_input}")

    async def get_recent_context(
        self, limit: int = 10, context_id: str = "default"
    ) -> list[dict[str, Any]]:
        """
        Retrieve recent conversation history.

        Args:
            limit: Maximum number of interactions to retrieve
            context_id: Session identifier

        Returns:
            List of recent interactions
        """
        if not self.connection:
            raise RuntimeError("Database connection not initialized")

        cursor = await self.connection.execute(
            """
            SELECT timestamp, user_input, intent_json, agent_response
            FROM conversations
            WHERE context_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (context_id, limit),
        )

        rows = await cursor.fetchall()
        results = []

        for row in rows:
            results.append(
                {
                    "timestamp": row[0],
                    "user_input": row[1],
                    "intent": json.loads(row[2]),
                    "response": row[3],
                }
            )

        return list(reversed(results))  # Return in chronological order

    async def search_similar(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> list[dict[str, Any]]:
        """
        Search for similar past interactions using vector embeddings.

        Args:
            query_embedding: Query vector
            k: Number of results to return

        Returns:
            List of similar interactions with similarity scores
        """
        if not self.connection:
            raise RuntimeError("Database connection not initialized")

        cursor = await self.connection.execute(
            """
            SELECT id, timestamp, user_input, intent_json, agent_response, embedding
            FROM conversations
            WHERE embedding IS NOT NULL
            """
        )

        rows = await cursor.fetchall()
        similarities = []

        for row in rows:
            stored_embedding = np.frombuffer(row[5], dtype=np.float32)
            similarity = self._cosine_similarity(query_embedding, stored_embedding)
            similarities.append((similarity, row))

        # Sort by similarity and return top k
        similarities.sort(reverse=True, key=lambda x: x[0])
        results = []

        for similarity, row in similarities[:k]:
            results.append(
                {
                    "similarity": float(similarity),
                    "timestamp": row[1],
                    "user_input": row[2],
                    "intent": json.loads(row[3]),
                    "response": row[4],
                }
            )

        return results

    async def clear_session(self, session_id: str) -> None:
        """
        Clear conversation history for a session.

        Args:
            session_id: Session identifier to clear
        """
        if not self.connection:
            raise RuntimeError("Database connection not initialized")

        await self.connection.execute(
            "DELETE FROM conversations WHERE context_id = ?", (session_id,)
        )
        await self.connection.execute(
            "DELETE FROM context WHERE session_id = ?", (session_id,)
        )
        await self.connection.commit()
        logger.info(f"Session cleared: {session_id}")

    async def prune_old_data(self, days: int = 30) -> None:
        """
        Remove conversation history older than specified days.

        Args:
            days: Number of days to retain
        """
        if not self.connection:
            raise RuntimeError("Database connection not initialized")

        cutoff_date = datetime.now() - timedelta(days=days)
        cursor = await self.connection.execute(
            "DELETE FROM conversations WHERE timestamp < ?", (cutoff_date,)
        )
        deleted_count = cursor.rowcount
        await self.connection.commit()
        logger.info(f"Pruned {deleted_count} old interactions")

    async def get_preference(self, key: str) -> Optional[str]:
        """
        Get a preference value.

        Args:
            key: Preference key

        Returns:
            Preference value or None
        """
        if not self.connection:
            raise RuntimeError("Database connection not initialized")

        cursor = await self.connection.execute(
            "SELECT value FROM preferences WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None

    async def set_preference(self, key: str, value: str) -> None:
        """
        Set a preference value.

        Args:
            key: Preference key
            value: Preference value
        """
        if not self.connection:
            raise RuntimeError("Database connection not initialized")

        await self.connection.execute(
            "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
            (key, value),
        )
        await self.connection.commit()

    async def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Memory store connection closed")

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Similarity score between -1 and 1
        """
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
