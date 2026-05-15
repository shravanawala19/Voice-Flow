from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, CloseEvent, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.app_controller import AppController
from settings.settings_manager import SettingsManager
from ui.floating_mic import FloatingMic
from ui.icons import app_icon, status_dot
from ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self, controller: AppController, settings_manager: SettingsManager) -> None:
        super().__init__()
        self.controller = controller
        self.settings_manager = settings_manager
        self.floating_mic = FloatingMic()
        self._recording = False

        self.setWindowTitle("VoiceFlow AI")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(760, 540)
        self.resize(880, 620)
        self._build_ui()
        self._build_tray()
        self._wire()

    def show_error(self, message: str) -> None:
        self.tray.showMessage("VoiceFlow AI", message, QSystemTrayIcon.MessageIcon.Warning, 5000)
        if self.isVisible():
            QMessageBox.warning(self, "VoiceFlow AI", message)

    def closeEvent(self, event: CloseEvent) -> None:
        if self.settings_manager.settings.minimize_to_tray and self.tray.isVisible():
            event.ignore()
            self.hide()
            self.tray.showMessage(
                "VoiceFlow AI",
                "Still running in the system tray.",
                QSystemTrayIcon.MessageIcon.Information,
                2500,
            )
            return
        self.controller.shutdown()
        event.accept()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        header = QHBoxLayout()
        title_group = QVBoxLayout()
        title = QLabel("VoiceFlow AI")
        title.setObjectName("Title")
        subtitle = QLabel("Global voice-to-text assistant")
        subtitle.setObjectName("Subtitle")
        title_group.addWidget(title)
        title_group.addWidget(subtitle)
        header.addLayout(title_group)
        header.addStretch()
        self.settings_button = QPushButton("Settings")
        self.settings_button.setFixedHeight(42)
        header.addWidget(self.settings_button)
        layout.addLayout(header)

        status_panel = QFrame()
        status_panel.setObjectName("Panel")
        status_layout = QHBoxLayout(status_panel)
        status_layout.setContentsMargins(18, 16, 18, 16)
        status_layout.setSpacing(14)

        self.status_dot = QLabel()
        self.status_dot.setPixmap(status_dot("#6f7a8a"))
        self.status_label = QLabel("Ready")
        self.status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("PrimaryButton")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("DangerButton")
        self.stop_button.setEnabled(False)
        status_layout.addWidget(self.status_dot)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.start_button)
        status_layout.addWidget(self.stop_button)
        layout.addWidget(status_panel)

        transcript_panel = QFrame()
        transcript_panel.setObjectName("Panel")
        transcript_layout = QVBoxLayout(transcript_panel)
        transcript_layout.setContentsMargins(18, 18, 18, 18)
        transcript_layout.setSpacing(10)
        transcript_title = QLabel("Live transcription")
        transcript_title.setObjectName("Subtitle")
        self.transcription = QTextEdit()
        self.transcription.setReadOnly(True)
        self.transcription.setPlaceholderText("Recognized text will appear here.")
        transcript_layout.addWidget(transcript_title)
        transcript_layout.addWidget(self.transcription)
        layout.addWidget(transcript_panel, stretch=1)

        self.setCentralWidget(root)

    def _build_tray(self) -> None:
        self.tray = QSystemTrayIcon(app_icon(), self)
        menu = QMenu()
        show_action = QAction("Show VoiceFlow AI", self)
        start_action = QAction("Start listening", self)
        stop_action = QAction("Stop listening", self)
        quit_action = QAction("Quit", self)
        show_action.triggered.connect(self._show_from_tray)
        start_action.triggered.connect(self.controller.start_listening)
        stop_action.triggered.connect(self.controller.stop_listening)
        quit_action.triggered.connect(self._quit)
        menu.addAction(show_action)
        menu.addSeparator()
        menu.addAction(start_action)
        menu.addAction(stop_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _wire(self) -> None:
        self.start_button.clicked.connect(self.controller.start_listening)
        self.stop_button.clicked.connect(self.controller.stop_listening)
        self.settings_button.clicked.connect(self._open_settings)
        self.controller.status_changed.connect(self._set_status)
        self.controller.recording_changed.connect(self._set_recording)
        self.controller.transcription_updated.connect(self._append_transcription)
        self.controller.level_changed.connect(self.floating_mic.set_level)
        self.controller.error.connect(self._set_error_status)

    def _set_status(self, status: str) -> None:
        self.status_label.setText(status)

    def _set_error_status(self, message: str) -> None:
        self.status_label.setText(message)
        self.status_dot.setPixmap(status_dot("#f25f5c"))

    def _set_recording(self, recording: bool) -> None:
        self._recording = recording
        self.start_button.setEnabled(not recording)
        self.stop_button.setEnabled(recording)
        self.status_dot.setPixmap(status_dot("#2fd1c5" if recording else "#6f7a8a"))
        self.tray.setIcon(app_icon(active=recording))
        if recording:
            self.floating_mic.start()
        else:
            self.floating_mic.stop()

    def _append_transcription(self, text: str) -> None:
        if not text.strip():
            return
        current = self.transcription.toPlainText().strip()
        next_text = f"{current}\n\n{text}" if current else text
        self.transcription.setPlainText(next_text)
        cursor = self.transcription.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.transcription.setTextCursor(cursor)

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.settings_manager, self)
        if dialog.exec():
            self.settings_manager.update(**dialog.values())
            self.controller.apply_settings()
            self.status_label.setText("Settings saved")

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_from_tray()

    def _show_from_tray(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def _quit(self) -> None:
        self.settings_manager.update(minimize_to_tray=False)
        self.controller.shutdown()
        QApplication.quit()
