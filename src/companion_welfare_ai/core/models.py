from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class DogProfile:
    id: int | None
    name: str
    breed: str = ""
    age_years: float | None = None
    notes: str = ""
    created_at_utc: str = field(default_factory=utc_now_iso)


@dataclass
class ConsentRecord:
    id: int | None
    dog_id: int
    consent_version: str
    granted: bool
    owner_name: str
    granted_at_utc: str = field(default_factory=utc_now_iso)


@dataclass
class VideoAsset:
    id: int | None
    dog_id: int
    original_filename: str
    stored_path: str
    fps: float
    frame_count: int
    duration_sec: float
    created_at_utc: str = field(default_factory=utc_now_iso)


@dataclass
class BehaviorEvent:
    id: int | None
    session_id: int
    label: str
    start_sec: float
    end_sec: float
    confidence: float
    is_manual: bool = False


@dataclass
class AnalysisSession:
    id: int | None
    dog_id: int
    video_id: int
    model_version: str
    status: str = "pending"
    summary: dict[str, Any] = field(default_factory=dict)
    created_at_utc: str = field(default_factory=utc_now_iso)