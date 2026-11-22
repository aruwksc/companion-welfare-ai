from __future__ import annotations

import os
from pathlib import Path

import cv2
import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from companion_welfare_ai.app.ui.main_window import MainWindow
from companion_welfare_ai.core.repositories import WelfareRepository
from companion_welfare_ai.core.services import CompanionWelfareService, NON_DIAGNOSTIC_NOTICE


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _make_sample_video(path: Path, frames: int = 12, fps: float = 10.0) -> Path:
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (64, 64))
    assert writer.isOpened()
    try:
        for idx in range(frames):
            frame = np.full((64, 64, 3), (idx * 20) % 255, dtype=np.uint8)
            writer.write(frame)
    finally:
        writer.release()
    return path


def test_sys01_sys02_sys03_consent_import_and_local_analysis(tmp_path: Path) -> None:
    svc = CompanionWelfareService(
        repository=WelfareRepository(tmp_path / "welfare.db"),
        data_dir=tmp_path / "store",
    )
    video_path = _make_sample_video(tmp_path / "walk.avi")

    dog = svc.create_dog("Rex", "Mix")
    assert dog.id is not None

    # SYS-01: record owner consent and import local video
    consent = svc.set_consent(dog.id, "Aidana", granted=True)
    assert consent.granted is True
    assert svc.has_consent(dog.id) is True

    asset = svc.import_video(dog.id, video_path)
    assert asset.id is not None
    assert Path(asset.stored_path).exists()

    # SYS-02: revoking/missing active consent blocks analysis
    svc.set_consent(dog.id, "Aidana", granted=False)
    assert svc.has_consent(dog.id) is False
    with pytest.raises(PermissionError):
        svc.run_analysis(dog.id, asset.id)

    # SYS-03: restore consent and run offline analysis
    svc.set_consent(dog.id, "Aidana", granted=True)
    session, events = svc.run_analysis(dog.id, asset.id)
    assert session.id is not None
    assert session.status == "completed"
    assert len(events) >= 1


def test_sys04_sys05_sys06_persistence_manual_events_and_report(tmp_path: Path) -> None:
    db_path = tmp_path / "welfare.db"
    store_dir = tmp_path / "store"
    svc = CompanionWelfareService(
        repository=WelfareRepository(db_path),
        data_dir=store_dir,
    )
    video_path = _make_sample_video(tmp_path / "clip.avi")

    dog = svc.create_dog("Boba", "Shepherd")
    assert dog.id is not None
    svc.set_consent(dog.id, "Aidana", True)
    asset = svc.import_video(dog.id, video_path)
    assert asset.id is not None

    session, _ = svc.run_analysis(dog.id, asset.id)
    assert session.id is not None

    # SYS-05: manual event annotation on timeline
    manual_ev = svc.add_manual_event(session.id, "head_shake", 0.2, 0.8)
    assert manual_ev.is_manual is True

    # SYS-06: report includes non-diagnostic notice and can be exported
    report = svc.build_report(session.id)
    assert NON_DIAGNOSTIC_NOTICE in report["non_diagnostic_notice"]
    assert any(ev["label"] == "head_shake" and ev["is_manual"] for ev in report["events"])

    exported = svc.export_report_markdown(session.id)
    assert exported.exists()
    assert NON_DIAGNOSTIC_NOTICE in exported.read_text(encoding="utf-8")

    # SYS-04: data persists across a new repository/service instance
    reloaded_svc = CompanionWelfareService(
        repository=WelfareRepository(db_path),
        data_dir=store_dir,
    )
    assert any(d.name == "Boba" for d in reloaded_svc.list_dogs())
    assert len(reloaded_svc.repository.list_events(session.id)) >= 2


def test_ui_mainwindow_smoke_and_report_banner(qapp: QApplication, tmp_path: Path) -> None:
    svc = CompanionWelfareService(
        repository=WelfareRepository(tmp_path / "ui.db"),
        data_dir=tmp_path / "ui_store",
    )
    win = MainWindow(service=svc)
    preview_text = win.report_preview.toPlainText()
    assert "non-diagnostic" in preview_text.lower()
    assert NON_DIAGNOSTIC_NOTICE.strip() in preview_text
    win.close()