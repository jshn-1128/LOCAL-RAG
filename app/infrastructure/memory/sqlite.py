"""
SQLite conversation memory adapter.

Purpose: Persist conversation history using SQLite.
Implements: MemoryPort
Dependencies: stdlib (sqlite3, json)

Lightweight embedded storage suitable for single-user deployments.
Future milestone: Milestone 15 — Conversation Memory.
"""

from app.domain.ports.memory import MemoryPort


class SQLiteMemory(MemoryPort):
    def __init__(self, db_path: str = "data/conversations.db") -> None:
        self._db_path = db_path
        self._connection = None
