"""Local SQLite storage adapter used by the CWA-28 packaging spike."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def default_data_dir() -> Path:
    """Return a per-user writable data directory without storing data in the install folder."""
    override = os.environ.get("COMPANION_WELFARE_AI_DATA_DIR")
    if override:
        return Path(override).expanduser()

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "CompanionWelfareAI"
    return Path.home() / ".local" / "share" / "companion-welfare-ai"


class SQLiteHelloRepository:
    """Small D4 storage proof: create, write, and read a local SQLite record."""

    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path or default_data_dir() / "hello-world.sqlite3"
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS hello_events (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       message TEXT NOT NULL,
                       created_at_utc TEXT NOT NULL
                   )"""
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def add_greeting(self, message: str = "Hello, companion!") -> int:
        """Persist a greeting and return the total number of saved greetings."""
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO hello_events (message, created_at_utc) VALUES (?, ?)",
                (message, timestamp),
            )
            count = connection.execute("SELECT COUNT(*) FROM hello_events").fetchone()[0]
        return int(count)
