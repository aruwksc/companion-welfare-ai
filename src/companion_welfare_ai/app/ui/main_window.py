from __future__ import annotations

import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from companion_welfare_ai.core.models import AnalysisSession, DogProfile, VideoAsset
from companion_welfare_ai.core.repositories import WelfareRepository, default_data_dir
from companion_welfare_ai.core.services import CompanionWelfareService, NON_DIAGNOSTIC_NOTICE


class MainWindow(QMainWindow):
    def __init__(self, service: CompanionWelfareService | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Companion Welfare AI — Desktop Review")
        self.resize(1180, 760)

        self.service = service or CompanionWelfareService(
            repository=WelfareRepository(default_data_dir() / "companion_welfare.sqlite3"),
            data_dir=default_data_dir(),
        )

        self._current_video: VideoAsset | None = None
        self._current_session: AnalysisSession | None = None
        self._cap: cv2.VideoCapture | None = None
        self._total_frames: int = 0
        self._fps: float = 25.0

        self._build_ui()
        self._refresh_dogs()

    def _build_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)

        notice_banner = QLabel(NON_DIAGNOSTIC_NOTICE)
        notice_banner.setWordWrap(True)
        notice_banner.setStyleSheet(
            "background-color: #2b2618; color: #f6d87e; padding: 8px 12px; border-radius: 6px;"
        )
        main_layout.addWidget(notice_banner)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter, stretch=1)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        profile_box = QGroupBox("1. Dog Profile & Owner Consent")
        profile_form = QFormLayout(profile_box)

        self.dog_combo = QComboBox()
        self.dog_combo.currentIndexChanged.connect(self._on_dog_selected)
        profile_form.addRow("Active Dog:", self.dog_combo)

        self.dog_name_input = QLineEdit()
        self.dog_name_input.setPlaceholderText("e.g. Rex")
        self.dog_breed_input = QLineEdit()
        self.dog_breed_input.setPlaceholderText("e.g. Labrador Mix")
        self.create_dog_btn = QPushButton("Create Profile")
        self.create_dog_btn.clicked.connect(self._on_create_dog)
        profile_form.addRow("New Name:", self.dog_name_input)
        profile_form.addRow("Breed:", self.dog_breed_input)
        profile_form.addRow("", self.create_dog_btn)

        self.owner_name_input = QLineEdit()
        self.owner_name_input.setPlaceholderText("Owner full name")
        self.consent_checkbox = QCheckBox("Owner grants local analysis consent")
        self.save_consent_btn = QPushButton("Save Consent")
        self.save_consent_btn.clicked.connect(self._on_save_consent)
        self.consent_status_label = QLabel("Consent: not granted")

        profile_form.addRow("Owner:", self.owner_name_input)
        profile_form.addRow("", self.consent_checkbox)
        profile_form.addRow("", self.save_consent_btn)
        profile_form.addRow("Status:", self.consent_status_label)
        left_layout.addWidget(profile_box)

        video_box = QGroupBox("2. Local Video & Offline Analysis")
        video_layout = QVBoxLayout(video_box)

        self.import_video_btn = QPushButton("Import Local Video...")
        self.import_video_btn.clicked.connect(self._on_import_video)
        video_layout.addWidget(self.import_video_btn)

        self.video_combo = QComboBox()
        self.video_combo.currentIndexChanged.connect(self._on_video_selected)
        video_layout.addWidget(self.video_combo)

        self.run_analysis_btn = QPushButton("Run Local Analysis")
        self.run_analysis_btn.clicked.connect(self._on_run_analysis)
        video_layout.addWidget(self.run_analysis_btn)

        self.session_meta_label = QLabel("Session: none")
        self.session_meta_label.setWordWrap(True)
        video_layout.addWidget(self.session_meta_label)

        left_layout.addWidget(video_box)
        left_layout.addStretch(1)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        preview_box = QGroupBox("3. Video Frame Review")
        preview_layout = QVBoxLayout(preview_box)
        self.frame_label = QLabel("No video loaded")
        self.frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_label.setMinimumHeight(210)
        self.frame_label.setStyleSheet("background-color: #141414; color: #bbbbbb; border-radius: 4px;")
        preview_layout.addWidget(self.frame_label)

        scrub_row = QHBoxLayout()
        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.setEnabled(False)
        self.frame_slider.valueChanged.connect(self._on_scrub_frame)
        self.time_label = QLabel("0.00s")
        scrub_row.addWidget(self.frame_slider, stretch=1)
        scrub_row.addWidget(self.time_label)
        preview_layout.addLayout(scrub_row)
        right_layout.addWidget(preview_box)

        timeline_box = QGroupBox("4. Event Timeline & Manual Annotation")
        timeline_layout = QVBoxLayout(timeline_box)

        self.events_table = QTableWidget(0, 5)
        self.events_table.setHorizontalHeaderLabels(
            ["Start (s)", "End (s)", "Label", "Confidence", "Source"]
        )
        self.events_table.cellClicked.connect(self._on_event_row_clicked)
        timeline_layout.addWidget(self.events_table)

        add_ev_row = QHBoxLayout()
        self.ev_start_input = QLineEdit()
        self.ev_start_input.setPlaceholderText("Start s (e.g. 1.0)")
        self.ev_end_input = QLineEdit()
        self.ev_end_input.setPlaceholderText("End s (e.g. 3.0)")
        self.ev_label_input = QLineEdit()
        self.ev_label_input.setPlaceholderText("Observation label")
        self.add_ev_btn = QPushButton("Add Event")
        self.add_ev_btn.clicked.connect(self._on_add_manual_event)
        add_ev_row.addWidget(self.ev_start_input)
        add_ev_row.addWidget(self.ev_end_input)
        add_ev_row.addWidget(self.ev_label_input)
        add_ev_row.addWidget(self.add_ev_btn)
        timeline_layout.addLayout(add_ev_row)
        right_layout.addWidget(timeline_box)

        report_box = QGroupBox("5. Report Preview & Export")
        report_layout = QVBoxLayout(report_box)
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        self.report_preview.setMaximumHeight(150)
        report_layout.addWidget(self.report_preview)

        report_btns = QHBoxLayout()
        self.refresh_report_btn = QPushButton("Preview Report")
        self.refresh_report_btn.clicked.connect(self._on_preview_report)
        self.export_report_btn = QPushButton("Export Markdown Report...")
        self.export_report_btn.clicked.connect(self._on_export_report)
        report_btns.addWidget(self.refresh_report_btn)
        report_btns.addWidget(self.export_report_btn)
        report_layout.addLayout(report_btns)
        right_layout.addWidget(report_box)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([380, 800])

    def _current_dog(self) -> DogProfile | None:
        data = self.dog_combo.currentData()
        return data if isinstance(data, DogProfile) else None

    def _refresh_dogs(self) -> None:
        self.dog_combo.blockSignals(True)
        self.dog_combo.clear()
        dogs = self.service.list_dogs()
        for d in dogs:
            self.dog_combo.addItem(f"#{d.id} — {d.name}", d)
        self.dog_combo.blockSignals(False)
        self._on_dog_selected()

    def _on_dog_selected(self) -> None:
        dog = self._current_dog()
        if dog is None or dog.id is None:
            self.consent_status_label.setText("Consent: no dog selected")
            self.video_combo.clear()
            return

        granted = self.service.has_consent(dog.id)
        self.consent_checkbox.setChecked(granted)
        self.consent_status_label.setText("Consent: GRANTED" if granted else "Consent: NOT GRANTED")

        self.video_combo.blockSignals(True)
        self.video_combo.clear()
        videos = self.service.repository.list_videos_for_dog(dog.id)
        for v in videos:
            self.video_combo.addItem(f"#{v.id} — {v.original_filename} ({v.duration_sec:.1f}s)", v)
        self.video_combo.blockSignals(False)
        self._on_video_selected()

    def _on_create_dog(self) -> None:
        try:
            dog = self.service.create_dog(
                name=self.dog_name_input.text(),
                breed=self.dog_breed_input.text(),
            )
            self.dog_name_input.clear()
            self.dog_breed_input.clear()
            self._refresh_dogs()
            idx = self.dog_combo.findData(dog)
            if idx >= 0:
                self.dog_combo.setCurrentIndex(idx)
        except Exception as exc:
            QMessageBox.warning(self, "Profile Error", str(exc))

    def _on_save_consent(self) -> None:
        dog = self._current_dog()
        if dog is None or dog.id is None:
            QMessageBox.warning(self, "Consent", "Select or create a dog profile first.")
            return
        try:
            self.service.set_consent(
                dog_id=dog.id,
                owner_name=self.owner_name_input.text(),
                granted=self.consent_checkbox.isChecked(),
            )
            self._on_dog_selected()
        except Exception as exc:
            QMessageBox.warning(self, "Consent Error", str(exc))

    def _on_import_video(self) -> None:
        dog = self._current_dog()
        if dog is None or dog.id is None:
            QMessageBox.warning(self, "Import Video", "Select a dog profile first.")
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Local Video",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)",
        )
        if not file_path:
            return
        try:
            asset = self.service.import_video(dog.id, file_path)
            self._on_dog_selected()
            idx = self.video_combo.findData(asset)
            if idx >= 0:
                self.video_combo.setCurrentIndex(idx)
        except Exception as exc:
            QMessageBox.warning(self, "Import Error", str(exc))

    def _on_video_selected(self) -> None:
        data = self.video_combo.currentData()
        self._current_video = data if isinstance(data, VideoAsset) else None
        if self._cap is not None:
            self._cap.release()
            self._cap = None

        if self._current_video is None:
            self.frame_slider.setEnabled(False)
            self.frame_label.setText("No video loaded")
            return

        cap = cv2.VideoCapture(self._current_video.stored_path)
        if not cap.isOpened():
            self.frame_slider.setEnabled(False)
            self.frame_label.setText("Unable to open video file")
            return

        self._cap = cap
        self._total_frames = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1))
        self._fps = float(cap.get(cv2.CAP_PROP_FPS) or self._current_video.fps or 25.0)
        self.frame_slider.setEnabled(True)
        self.frame_slider.setRange(0, self._total_frames - 1)
        self.frame_slider.setValue(0)
        self._render_frame(0)

    def _render_frame(self, frame_idx: int) -> None:
        if self._cap is None:
            return
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = self._cap.read()
        if not ok or frame is None:
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.frame_label.width() or 480,
            self.frame_label.height() or 220,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.frame_label.setPixmap(pixmap)
        sec = frame_idx / (self._fps if self._fps > 0 else 25.0)
        self.time_label.setText(f"{sec:.2f}s")

    def _on_scrub_frame(self, value: int) -> None:
        self._render_frame(value)

    def _on_run_analysis(self) -> None:
        dog = self._current_dog()
        if dog is None or dog.id is None or self._current_video is None or self._current_video.id is None:
            QMessageBox.warning(self, "Analysis", "Select a dog profile and an imported video first.")
            return
        try:
            session, events = self.service.run_analysis(dog.id, self._current_video.id)
            self._current_session = session
            self.session_meta_label.setText(
                f"Session #{session.id} | status: {session.status} | model: {session.model_version}"
            )
            self._populate_events()
            self._on_preview_report()
            if not events:
                QMessageBox.information(self, "Analysis", "Analysis completed with no events.")
        except Exception as exc:
            QMessageBox.warning(self, "Analysis Error", str(exc))

    def _populate_events(self) -> None:
        self.events_table.setRowCount(0)
        if self._current_session is None or self._current_session.id is None:
            return
        events = self.service.repository.list_events(self._current_session.id)
        for row_idx, ev in enumerate(events):
            self.events_table.insertRow(row_idx)
            self.events_table.setItem(row_idx, 0, QTableWidgetItem(f"{ev.start_sec:.2f}"))
            self.events_table.setItem(row_idx, 1, QTableWidgetItem(f"{ev.end_sec:.2f}"))
            self.events_table.setItem(row_idx, 2, QTableWidgetItem(ev.label))
            self.events_table.setItem(row_idx, 3, QTableWidgetItem(f"{ev.confidence:.2f}"))
            self.events_table.setItem(
                row_idx, 4, QTableWidgetItem("manual" if ev.is_manual else "model")
            )

    def _on_event_row_clicked(self, row: int, _col: int) -> None:
        item = self.events_table.item(row, 0)
        if not item or not self.frame_slider.isEnabled():
            return
        try:
            start_sec = float(item.text())
            frame_idx = int(round(start_sec * (self._fps if self._fps > 0 else 25.0)))
            frame_idx = max(0, min(self._total_frames - 1, frame_idx))
            self.frame_slider.setValue(frame_idx)
        except ValueError:
            pass

    def _on_add_manual_event(self) -> None:
        if self._current_session is None or self._current_session.id is None:
            QMessageBox.warning(self, "Manual Event", "Run or select an analysis session first.")
            return
        try:
            start_sec = float(self.ev_start_input.text().strip())
            end_sec = float(self.ev_end_input.text().strip())
            label = self.ev_label_input.text().strip()
            if not label:
                raise ValueError("Observation label must not be empty")
            self.service.add_manual_event(self._current_session.id, label, start_sec, end_sec)
            self.ev_start_input.clear()
            self.ev_end_input.clear()
            self.ev_label_input.clear()
            self._populate_events()
            self._on_preview_report()
        except Exception as exc:
            QMessageBox.warning(self, "Event Error", str(exc))

    def _on_preview_report(self) -> None:
        if self._current_session is None or self._current_session.id is None:
            self.report_preview.setPlainText(NON_DIAGNOSTIC_NOTICE)
            return
        report = self.service.build_report(self._current_session.id)
        lines = [
            f"Session #{report['session_id']} | Model: {report['model_version']} | Status: {report['status']}",
            report["non_diagnostic_notice"],
            "",
            "Events:",
        ]
        for ev in report["events"]:
            src = "manual" if ev["is_manual"] else "model"
            lines.append(
                f"  - [{ev['start_sec']:.2f}s - {ev['end_sec']:.2f}s] {ev['label']} "
                f"(conf={ev['confidence']:.2f}, {src})"
            )
        self.report_preview.setPlainText("\n".join(lines))

    def _on_export_report(self) -> None:
        if self._current_session is None or self._current_session.id is None:
            QMessageBox.warning(self, "Export Report", "Run an analysis session before exporting a report.")
            return
        default_name = str(self.service.reports_dir / f"session_{self._current_session.id}_report.md")
        target_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Markdown Report",
            default_name,
            "Markdown Files (*.md);;All Files (*)",
        )
        if not target_path:
            return
        try:
            out = self.service.export_report_markdown(self._current_session.id, target_path)
            QMessageBox.information(self, "Report Exported", f"Saved report to:\n{out}")
        except Exception as exc:
            QMessageBox.warning(self, "Export Error", str(exc))

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        super().closeEvent(event)