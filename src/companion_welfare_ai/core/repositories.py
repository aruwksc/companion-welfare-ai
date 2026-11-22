"""Local SQLite storage adapter used by the CWA-28 packaging spike and CWA-24 repository."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from companion_welfare_ai.core.models import (
    AnalysisSession,
    BehaviorEvent,
    ConsentRecord,
    DogProfile,
    VideoAsset,
)


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


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dog_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    breed TEXT NOT NULL DEFAULT '',
    age_years REAL,
    notes TEXT NOT NULL DEFAULT '',
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS consent_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dog_id INTEGER NOT NULL REFERENCES dog_profiles(id) ON DELETE CASCADE,
    consent_version TEXT NOT NULL,
    granted INTEGER NOT NULL,
    owner_name TEXT NOT NULL,
    granted_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS video_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dog_id INTEGER NOT NULL REFERENCES dog_profiles(id) ON DELETE CASCADE,
    original_filename TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    fps REAL NOT NULL,
    frame_count INTEGER NOT NULL,
    duration_sec REAL NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analysis_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dog_id INTEGER NOT NULL REFERENCES dog_profiles(id) ON DELETE CASCADE,
    video_id INTEGER NOT NULL REFERENCES video_assets(id) ON DELETE CASCADE,
    model_version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    summary_json TEXT NOT NULL DEFAULT '{}',
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS behavior_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    start_sec REAL NOT NULL,
    end_sec REAL NOT NULL,
    confidence REAL NOT NULL,
    is_manual INTEGER NOT NULL DEFAULT 0
);
"""


class WelfareRepository:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path is not None else default_data_dir() / "companion_welfare.sqlite3"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)

    def create_dog_profile(self, profile: DogProfile) -> DogProfile:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO dog_profiles (name, breed, age_years, notes, created_at_utc)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    profile.name,
                    profile.breed,
                    profile.age_years,
                    profile.notes,
                    profile.created_at_utc,
                ),
            )
            profile.id = int(cur.lastrowid)
        return profile

    def list_dog_profiles(self) -> list[DogProfile]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM dog_profiles ORDER BY id DESC").fetchall()
        return [
            DogProfile(
                id=int(r["id"]),
                name=r["name"],
                breed=r["breed"],
                age_years=r["age_years"],
                notes=r["notes"],
                created_at_utc=r["created_at_utc"],
            )
            for r in rows
        ]

    def record_consent(self, consent: ConsentRecord) -> ConsentRecord:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO consent_records (dog_id, consent_version, granted, owner_name, granted_at_utc)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    consent.dog_id,
                    consent.consent_version,
                    1 if consent.granted else 0,
                    consent.owner_name,
                    consent.granted_at_utc,
                ),
            )
            consent.id = int(cur.lastrowid)
        return consent

    def has_active_consent(self, dog_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT granted FROM consent_records
                WHERE dog_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (dog_id,),
            ).fetchone()
        return bool(row and row["granted"] == 1)

    def add_video_asset(self, video: VideoAsset) -> VideoAsset:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO video_assets (
                    dog_id, original_filename, stored_path, fps, frame_count, duration_sec, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    video.dog_id,
                    video.original_filename,
                    video.stored_path,
                    video.fps,
                    video.frame_count,
                    video.duration_sec,
                    video.created_at_utc,
                ),
            )
            video.id = int(cur.lastrowid)
        return video

    def get_video_asset(self, video_id: int) -> VideoAsset | None:
        with self._connect() as conn:
            r = conn.execute("SELECT * FROM video_assets WHERE id = ?", (video_id,)).fetchone()
        if not r:
            return None
        return VideoAsset(
            id=int(r["id"]),
            dog_id=int(r["dog_id"]),
            original_filename=r["original_filename"],
            stored_path=r["stored_path"],
            fps=float(r["fps"]),
            frame_count=int(r["frame_count"]),
            duration_sec=float(r["duration_sec"]),
            created_at_utc=r["created_at_utc"],
        )

    def list_videos_for_dog(self, dog_id: int) -> list[VideoAsset]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM video_assets WHERE dog_id = ? ORDER BY id DESC", (dog_id,)
            ).fetchall()
        return [
            VideoAsset(
                id=int(r["id"]),
                dog_id=int(r["dog_id"]),
                original_filename=r["original_filename"],
                stored_path=r["stored_path"],
                fps=float(r["fps"]),
                frame_count=int(r["frame_count"]),
                duration_sec=float(r["duration_sec"]),
                created_at_utc=r["created_at_utc"],
            )
            for r in rows
        ]

    def create_session(self, session: AnalysisSession) -> AnalysisSession:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO analysis_sessions (
                    dog_id, video_id, model_version, status, summary_json, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session.dog_id,
                    session.video_id,
                    session.model_version,
                    session.status,
                    json.dumps(session.summary, ensure_ascii=False),
                    session.created_at_utc,
                ),
            )
            session.id = int(cur.lastrowid)
        return session

    def update_session_result(
        self, session_id: int, status: str, summary: dict, model_version: str | None = None
    ) -> None:
        with self._connect() as conn:
            if model_version is not None:
                conn.execute(
                    """
                    UPDATE analysis_sessions
                    SET status = ?, summary_json = ?, model_version = ?
                    WHERE id = ?
                    """,
                    (status, json.dumps(summary, ensure_ascii=False), model_version, session_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE analysis_sessions
                    SET status = ?, summary_json = ?
                    WHERE id = ?
                    """,
                    (status, json.dumps(summary, ensure_ascii=False), session_id),
                )

    def get_session(self, session_id: int) -> AnalysisSession | None:
        with self._connect() as conn:
            r = conn.execute("SELECT * FROM analysis_sessions WHERE id = ?", (session_id,)).fetchone()
        if not r:
            return None
        return AnalysisSession(
            id=int(r["id"]),
            dog_id=int(r["dog_id"]),
            video_id=int(r["video_id"]),
            model_version=r["model_version"],
            status=r["status"],
            summary=json.loads(r["summary_json"] or "{}"),
            created_at_utc=r["created_at_utc"],
        )

    def list_sessions_for_dog(self, dog_id: int) -> list[AnalysisSession]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM analysis_sessions WHERE dog_id = ? ORDER BY id DESC", (dog_id,)
            ).fetchall()
        return [
            AnalysisSession(
                id=int(r["id"]),
                dog_id=int(r["dog_id"]),
                video_id=int(r["video_id"]),
                model_version=r["model_version"],
                status=r["status"],
                summary=json.loads(r["summary_json"] or "{}"),
                created_at_utc=r["created_at_utc"],
            )
            for r in rows
        ]

    def replace_session_events(self, session_id: int, events: list[BehaviorEvent]) -> list[BehaviorEvent]:
        saved: list[BehaviorEvent] = []
        with self._connect() as conn:
            conn.execute("DELETE FROM behavior_events WHERE session_id = ?", (session_id,))
            for ev in events:
                cur = conn.execute(
                    """
                    INSERT INTO behavior_events (
                        session_id, label, start_sec, end_sec, confidence, is_manual
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        ev.label,
                        ev.start_sec,
                        ev.end_sec,
                        ev.confidence,
                        1 if ev.is_manual else 0,
                    ),
                )
                ev.session_id = session_id
                ev.id = int(cur.lastrowid)
                saved.append(ev)
        return saved

    def add_event(self, event: BehaviorEvent) -> BehaviorEvent:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO behavior_events (
                    session_id, label, start_sec, end_sec, confidence, is_manual
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.session_id,
                    event.label,
                    event.start_sec,
                    event.end_sec,
                    event.confidence,
                    1 if event.is_manual else 0,
                ),
            )
            event.id = int(cur.lastrowid)
        return event

    def update_event(self, event: BehaviorEvent) -> None:
        if event.id is None:
            raise ValueError("BehaviorEvent.id is required for update")
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE behavior_events
                SET label = ?, start_sec = ?, end_sec = ?, confidence = ?, is_manual = ?
                WHERE id = ?
                """,
                (
                    event.label,
                    event.start_sec,
                    event.end_sec,
                    event.confidence,
                    1 if event.is_manual else 0,
                    event.id,
                ),
            )

    def delete_event(self, event_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM behavior_events WHERE id = ?", (event_id,))

    def list_events(self, session_id: int) -> list[BehaviorEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM behavior_events WHERE session_id = ? ORDER BY start_sec ASC, id ASC",
                (session_id,),
            ).fetchall()
        return [
            BehaviorEvent(
                id=int(r["id"]),
                session_id=int(r["session_id"]),
                label=r["label"],
                start_sec=float(r["start_sec"]),
                end_sec=float(r["end_sec"]),
                confidence=float(r["confidence"]),
                is_manual=bool(r["is_manual"]),
            )
            for r in rows
        ]