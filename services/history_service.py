from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from settings.settings_manager import app_data_dir


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class HistoryEntry:
    id: int
    created_at: str
    mode: str
    language: str
    text: str
    target_window: str


class HistoryService:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or app_data_dir() / "history.db"
        self._init_db()

    def add(self, text: str, mode: str, language: str, target_window: str) -> None:
        if not text.strip():
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO speech_history(created_at, mode, language, text, target_window)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (datetime.now(timezone.utc).isoformat(timespec="seconds"), mode, language, text, target_window),
                )
        except sqlite3.Error:
            LOGGER.exception("Unable to save speech history")

    def latest(self, limit: int = 100) -> list[HistoryEntry]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute(
                    """
                    SELECT id, created_at, mode, language, text, target_window
                    FROM speech_history
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            return [HistoryEntry(*row) for row in rows]
        except sqlite3.Error:
            LOGGER.exception("Unable to load speech history")
            return []

    def _init_db(self) -> None:
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS speech_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TEXT NOT NULL,
                        mode TEXT NOT NULL,
                        language TEXT NOT NULL,
                        text TEXT NOT NULL,
                        target_window TEXT NOT NULL
                    )
                    """
                )
        except sqlite3.Error:
            LOGGER.exception("Unable to initialize speech history database")
