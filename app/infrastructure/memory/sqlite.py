"""
SQLite conversation memory adapter.

Purpose: Persist conversation history using SQLite.
Implements: MemoryPort
Dependencies: stdlib (sqlite3, json)

Lightweight embedded storage suitable for single-user deployments.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import UUID

from app.domain.models.conversation import Conversation, Message
from app.domain.ports.memory import MemoryPort

logger = logging.getLogger(__name__)


class SQLiteMemory(MemoryPort):
    def __init__(self, db_path: str = "data/conversations.db") -> None:
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None

    async def save_conversation(self, conversation: Conversation) -> None:
        conn = self._get_connection()
        conv_id = str(conversation.id)
        messages_json = json.dumps(
            [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in conversation.messages
            ]
        )
        metadata_json = json.dumps(conversation.metadata or {})

        conn.execute(
            """INSERT OR REPLACE INTO conversations (id, messages, metadata)
               VALUES (?, ?, ?)""",
            (conv_id, messages_json, metadata_json),
        )
        conn.commit()

    async def get_conversation(self, conversation_id: str) -> Conversation | None:
        conn = self._get_connection()
        row = conn.execute(
            "SELECT id, messages, metadata FROM conversations WHERE id = ?",
            (conversation_id,),
        ).fetchone()
        if row is None:
            return None

        conv_id, messages_json, metadata_json = row
        messages_data = json.loads(messages_json)
        messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
            )
            for msg in messages_data
        ]
        metadata = json.loads(metadata_json) if metadata_json else None

        return Conversation(
            id=UUID(conv_id),
            messages=messages,
            metadata=metadata,
        )

    async def list_conversations(self) -> list[Conversation]:
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT id, messages, metadata FROM conversations ORDER BY rowid DESC"
        ).fetchall()

        conversations: list[Conversation] = []
        for row in rows:
            conv_id, messages_json, metadata_json = row
            messages_data = json.loads(messages_json)
            messages = [
                Message(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=datetime.fromisoformat(msg["timestamp"]),
                )
                for msg in messages_data
            ]
            metadata = json.loads(metadata_json) if metadata_json else None
            conversations.append(
                Conversation(
                    id=UUID(conv_id),
                    messages=messages,
                    metadata=metadata,
                )
            )
        return conversations

    async def delete_conversation(self, conversation_id: str) -> None:
        conn = self._get_connection()
        conn.execute(
            "DELETE FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            db_path = Path(self._db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(str(db_path))
            self._connection.execute("""CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    messages TEXT NOT NULL,
                    metadata TEXT
                )""")
            logger.info("SQLite memory initialized: %s", self._db_path)
        return self._connection
