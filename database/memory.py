"""
Memory Store - SQLite-based storage for messages, summaries, and tasks.

This implements the ContextProvider protocol for future upgradability to LangChain/RAG.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite


class MemoryStore:
    """
    SQLite-based memory store for messages, summaries, and tasks.

    Stores:
    - Incoming messages from Gmail/Slack
    - LLM-generated summaries
    - Extracted tasks
    - Processing metadata
    """

    def __init__(self
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        """Initialize database and create tables."""
        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db = await aiosqlite.connect(self.db_path)
        await self._create_tables()

    async def _create_tables(self) -> None:
        """Create database schema."""

        # Messages table - stores raw incoming messages
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                sender TEXT NOT NULL,
                subject TEXT,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                raw_data TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(id, source)
            )
        """)

        # Summaries table - stores LLM-generated summaries
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                summary TEXT NOT NULL,
                model_used TEXT,
                generated_at TEXT NOT NULL,
                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
        """)

        # Tasks table - stores extracted tasks
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                summary_id INTEGER,
                task_text TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                deadline TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY (message_id) REFERENCES messages(id),
                FOREIGN KEY (summary_id) REFERENCES summaries(id)
            )
        """)

        # Context table - stores conversation context for LLM
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                interaction_type TEXT NOT NULL,
                user_input TEXT,
                llm_response TEXT,
                embedding BLOB,
                timestamp TEXT NOT NULL
            )
        """)

        # Indexes for performance
        await self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_source ON messages(source)"
        )
        await self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)"
        )
        await self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)"
        )
        await self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_context_session ON context(session_id)"
        )

        await self.db.commit()

    async def store_message(
        self,
        message_id: str,
        source: str,
        sender: str,
        content: str,
        subject: Optional[str] = None,
        timestamp: Optional[str] = None,
        raw_data: Optional[Dict] = None,
    ) -> None:
        """Store incoming message."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        await self.db.execute(
            """
            INSERT OR REPLACE INTO messages
            (id, source, sender, subject, content, timestamp, raw_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                message_id,
                source,
                sender,
                subject,
                content,
                timestamp,
                json.dumps(raw_data) if raw_data else None,
                datetime.now().isoformat(),
            ),
        )
        await self.db.commit()

    async def store_summary(
        self, message_id: str, summary: str, model_used: str = "unknown"
    ) -> int:
        """Store LLM-generated summary. Returns summary_id."""
        cursor = await self.db.execute(
            """
            INSERT INTO summaries (message_id, summary, model_used, generated_at)
            VALUES (?, ?, ?, ?)
        """,
            (message_id, summary, model_used, datetime.now().isoformat()),
        )
        await self.db.commit()
        return cursor.lastrowid

    async def store_tasks(
        self,
        message_id: str,
        tasks: List[str],
        summary_id: Optional[int] = None,
        priorities: Optional[List[int]] = None,
    ) -> List[int]:
        """Store extracted tasks. Returns list of task_ids."""
        task_ids = []

        if priorities is None:
            priorities = [0] * len(tasks)

        for task_text, priority in zip(tasks, priorities):
            cursor = await self.db.execute(
                """
                INSERT INTO tasks (message_id, summary_id, task_text, priority, status, created_at)
                VALUES (?, ?, ?, ?, 'pending', ?)
            """,
                (
                    message_id,
                    summary_id,
                    task_text,
                    priority,
                    datetime.now().isoformat(),
                ),
            )
            task_ids.append(cursor.lastrowid)

        await self.db.commit()
        return task_ids

    async def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve message by ID."""
        cursor = await self.db.execute(
            "SELECT * FROM messages WHERE id = ?", (message_id,)
        )
        row = await cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    async def get_summary(self, message_id: str) -> Optional[str]:
        """Retrieve summary for a message."""
        cursor = await self.db.execute(
            "SELECT summary FROM summaries WHERE message_id = ? ORDER BY generated_at DESC LIMIT 1",
            (message_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else None

    async def get_tasks(
        self, message_id: str, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve tasks for a message."""
        if status:
            cursor = await self.db.execute(
                "SELECT * FROM tasks WHERE message_id = ? AND status = ? ORDER BY priority DESC",
                (message_id, status),
            )
        else:
            cursor = await self.db.execute(
                "SELECT * FROM tasks WHERE message_id = ? ORDER BY priority DESC",
                (message_id,),
            )

        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def get_recent_messages(
        self, limit: int = 10, source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve recent messages."""
        if source:
            cursor = await self.db.execute(
                "SELECT * FROM messages WHERE source = ? ORDER BY timestamp DESC LIMIT ?",
                (source, limit),
            )
        else:
            cursor = await self.db.execute(
                "SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?", (limit,)
            )

        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def get_pending_tasks(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve all pending tasks across all messages."""
        if limit:
            cursor = await self.db.execute(
                "SELECT * FROM tasks WHERE status = 'pending' ORDER BY priority DESC, created_at ASC LIMIT ?",
                (limit,),
            )
        else:
            cursor = await self.db.execute(
                "SELECT * FROM tasks WHERE status = 'pending' ORDER BY priority DESC, created_at ASC"
            )

        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def update_task_status(self, task_id: int, status: str) -> None:
        """Update task status (pending/in_progress/completed/cancelled)."""
        completed_at = datetime.now().isoformat() if status == "completed" else None
        await self.db.execute(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (status, completed_at, task_id),
        )
        await self.db.commit()

    async def store_context(
        self,
        interaction_type: str,
        user_input: Optional[str] = None,
        llm_response: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Store interaction context for LLM memory."""
        await self.db.execute(
            """
            INSERT INTO context (session_id, interaction_type, user_input, llm_response, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                session_id,
                interaction_type,
                user_input,
                llm_response,
                datetime.now().isoformat(),
            ),
        )
        await self.db.commit()

    async def get_recent_context(
        self, limit: int = 10, session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve recent context for LLM."""
        if session_id:
            cursor = await self.db.execute(
                "SELECT * FROM context WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit),
            )
        else:
            cursor = await self.db.execute(
                "SELECT * FROM context ORDER BY timestamp DESC LIMIT ?", (limit,)
            )

        rows = await cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def close(self) -> None:
        """Close database connection."""
        if self.db:
            await self.db.close()
