from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from companion_welfare_ai.core.models import (
    AnalysisSession,
    BehaviorEvent,
    ConsentRecord,
    DogProfile,
    VideoAsset,
)
from companion_welfare_ai.core.ports import BehaviourPort, PosePort
from companion_welfare_ai.core.repositories import WelfareRepository, default_data_dir

NON_DIAGNOSTIC_NOTICE = (
    "Non-diagnostic notice: Behaviour outputs describe observable movement and posture patterns "
    "with model uncertainty and do not constitute a veterinary diagnosis."
)


class _DefaultPoseAdapter:
    model_version = "pose-stub-v0.1"

    def estimate_pose(self, frame: np.ndarray) -> dict[str, Any]:
        h, w = frame.shape[:2] if frame is not None and frame.size > 0 else (0, 0)
        mean_intensity = float(np.mean(frame)) if frame is not None and frame.size > 0 else 0.0
        return {"width": w, "height": h, "mean_intensity": mean_intensity, "keypoints": []}


class _DefaultBehaviourAdapter:
    model_version = "behaviour-heuristic-v0.1"

    def predict_events(
        self,
        frames: list[np.ndarray],
        poses: list[dict[str, Any]],
        fps: float,
    ) -> list[dict[str, Any]]:
        if not frames:
            return []
        safe_fps = fps if fps and fps > 0 else 1.0
        duration_sec = round(len(frames) / safe_fps, 2)
        intensities = [float(p.get("mean_intensity", 0.0)) for p in poses]
        diffs = [
            abs(intensities[i] - intensities[i - 1]) for i in range(1, len(intensities))
        ]
        avg_motion = float(np.mean(diffs)) if diffs else 0.0

        if avg_motion > 4.0:
            label = "active_movement"
            confidence = 0.68
        else:
            label = "resting_or_low_motion"
            confidence = 0.62

        return [
            {
                "label": label,
                "start_sec": 0.0,
                "end_sec": max(0.5, duration_sec),
                "confidence": confidence,
            }
        ]


class CompanionWelfareService:
    """Application service mediating UI commands, local storage, local analysis, and reports."""

    def __init__(
        self,
        repository: WelfareRepository,
        data_dir: Path | None = None,
        pose_adapter: PosePort | None = None,
        behaviour_adapter: BehaviourPort | None = None,
        sample_stride: int = 5,
    ) -> None:
        self.repository = repository
        self.data_dir = Path(data_dir) if data_dir is not None else default_data_dir()
        self.videos_dir = self.data_dir / "videos"
        self.reports_dir = self.data_dir / "reports"
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.pose_adapter: PosePort = pose_adapter or _DefaultPoseAdapter()
        self.behaviour_adapter: BehaviourPort = behaviour_adapter or _DefaultBehaviourAdapter()
        self.sample_stride = max(1, int(sample_stride))

    def create_dog(self, name: str, breed: str = "", age_years: float | None = None, notes: str = "") -> DogProfile:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Dog name must not be empty")
        profile = DogProfile(
            id=None,
            name=clean_name,
            breed=breed.strip(),
            age_years=age_years,
            notes=notes.strip(),
        )
        return self.repository.create_dog_profile(profile)

    def list_dogs(self) -> list[DogProfile]:
        return self.repository.list_dog_profiles()

    def set_consent(
        self,
        dog_id: int,
        owner_name: str,
        granted: bool,
        consent_version: str = "1.0",
    ) -> ConsentRecord:
        if not owner_name.strip():
            raise ValueError("Owner name is required to record consent")
        record = ConsentRecord(
            id=None,
            dog_id=dog_id,
            consent_version=consent_version.strip() or "1.0",
            granted=bool(granted),
            owner_name=owner_name.strip(),
        )
        return self.repository.record_consent(record)

    def has_consent(self, dog_id: int) -> bool:
        return self.repository.has_active_consent(dog_id)

    def import_video(self, dog_id: int, source_video_path: str | Path) -> VideoAsset:
        """Copy video locally into user-owned storage and inspect metadata using OpenCV (SYS-01)."""
        if not self.has_consent(dog_id):
            raise PermissionError("Active owner consent is required before importing video for analysis")

        src = Path(source_video_path)
        if not src.exists() or not src.is_file():
            raise FileNotFoundError(f"Video file not found: {src}")

        dog_video_dir = self.videos_dir / f"dog_{dog_id}"
        dog_video_dir.mkdir(parents=True, exist_ok=True)
        target_path = dog_video_dir / src.name
        if target_path.exists():
            stem = src.stem
            suffix = src.suffix
            idx = 1
            while target_path.exists():
                target_path = dog_video_dir / f"{stem}_{idx}{suffix}"
                idx += 1

        shutil.copy2(src, target_path)

        cap = cv2.VideoCapture(str(target_path))
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        cap.release()

        safe_fps = fps if fps > 0 else 25.0
        duration_sec = round(frame_count / safe_fps, 3) if frame_count > 0 else 0.0

        asset = VideoAsset(
            id=None,
            dog_id=dog_id,
            original_filename=src.name,
            stored_path=str(target_path),
            fps=safe_fps,
            frame_count=frame_count,
            duration_sec=duration_sec,
        )
        return self.repository.add_video_asset(asset)

    def _sample_frames(self, video_path: Path) -> list[np.ndarray]:
        cap = cv2.VideoCapture(str(video_path))
        frames: list[np.ndarray] = []
        idx = 0
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                if idx % self.sample_stride == 0:
                    frames.append(frame)
                idx += 1
        finally:
            cap.release()
        return frames

    def run_analysis(self, dog_id: int, video_id: int) -> tuple[AnalysisSession, list[BehaviorEvent]]:
        """Run local frame sampling, pose estimation, and behaviour prediction (SYS-03, SYS-05)."""
        if not self.has_consent(dog_id):
            raise PermissionError("Active owner consent is required to run analysis")

        video = self.repository.get_video_asset(video_id)
        if video is None:
            raise ValueError(f"Video asset {video_id} not found")

        model_version = f"{self.pose_adapter.model_version}+{self.behaviour_adapter.model_version}"
        session = self.repository.create_session(
            AnalysisSession(
                id=None,
                dog_id=dog_id,
                video_id=video_id,
                model_version=model_version,
                status="running",
                summary={},
            )
        )

        try:
            frames = self._sample_frames(Path(video.stored_path))
            effective_fps = (video.fps or 25.0) / self.sample_stride
            poses = [self.pose_adapter.estimate_pose(f) for f in frames]
            raw_events = self.behaviour_adapter.predict_events(frames, poses, effective_fps)

            events: list[BehaviorEvent] = []
            for item in raw_events:
                events.append(
                    BehaviorEvent(
                        id=None,
                        session_id=int(session.id),
                        label=str(item["label"]),
                        start_sec=float(item["start_sec"]),
                        end_sec=float(item["end_sec"]),
                        confidence=float(item["confidence"]),
                        is_manual=False,
                    )
                )

            saved_events = self.repository.replace_session_events(int(session.id), events)
            summary = {
                "sampled_frames": len(frames),
                "event_count": len(saved_events),
                "non_diagnostic_notice": NON_DIAGNOSTIC_NOTICE,
            }
            self.repository.update_session_result(
                int(session.id),
                status="completed",
                summary=summary,
                model_version=model_version,
            )
            updated_session = self.repository.get_session(int(session.id))
            assert updated_session is not None
            return updated_session, saved_events
        except Exception as exc:
            self.repository.update_session_result(
                int(session.id),
                status="failed",
                summary={"error": str(exc), "non_diagnostic_notice": NON_DIAGNOSTIC_NOTICE},
            )
            raise

    def add_manual_event(
        self,
        session_id: int,
        label: str,
        start_sec: float,
        end_sec: float,
        confidence: float = 1.0,
    ) -> BehaviorEvent:
        if end_sec < start_sec:
            raise ValueError("end_sec must be greater than or equal to start_sec")
        ev = BehaviorEvent(
            id=None,
            session_id=session_id,
            label=label.strip(),
            start_sec=float(start_sec),
            end_sec=float(end_sec),
            confidence=float(confidence),
            is_manual=True,
        )
        return self.repository.add_event(ev)

    def build_report(self, session_id: int) -> dict[str, Any]:
        session = self.repository.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        events = self.repository.list_events(session_id)
        return {
            "session_id": session.id,
            "dog_id": session.dog_id,
            "video_id": session.video_id,
            "model_version": session.model_version,
            "status": session.status,
            "non_diagnostic_notice": NON_DIAGNOSTIC_NOTICE,
            "events": [
                {
                    "id": e.id,
                    "label": e.label,
                    "start_sec": e.start_sec,
                    "end_sec": e.end_sec,
                    "confidence": e.confidence,
                    "is_manual": e.is_manual,
                }
                for e in events
            ],
        }

    def export_report_markdown(self, session_id: int, output_path: str | Path | None = None) -> Path:
        report = self.build_report(session_id)
        target = (
            Path(output_path)
            if output_path is not None
            else self.reports_dir / f"session_{session_id}_report.md"
        )
        target.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            f"# Companion Welfare Observation Report (Session #{report['session_id']})",
            "",
            f"- **Dog ID:** {report['dog_id']}",
            f"- **Video ID:** {report['video_id']}",
            f"- **Model version:** `{report['model_version']}`",
            f"- **Status:** {report['status']}",
            "",
            f"> {report['non_diagnostic_notice']}",
            "",
            "## Observed Events",
            "",
        ]
        if not report["events"]:
            lines.append("_No behaviour events recorded._")
        else:
            lines.append("| Interval (s) | Label | Confidence | Source |")
            lines.append("|---|---|---:|---|")
            for ev in report["events"]:
                src_label = "manual" if ev["is_manual"] else "model"
                lines.append(
                    f"| {ev['start_sec']:.2f} - {ev['end_sec']:.2f} | {ev['label']} | {ev['confidence']:.2f} | {src_label} |"
                )

        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return target