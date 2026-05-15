from __future__ import annotations

import logging
import time
from typing import Protocol

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

from audio.recorder import AudioRecorder
from services.ai_service import AIService
from services.history_service import HistoryService
from services.hotkey_service import HotkeyService
from services.startup_service import StartupService
from services.text_processor import TextProcessor
from services.transcription_worker import TranscriptionWorker
from services.typing_service import TypingService
from services.window_service import WindowService
from settings.settings_manager import SettingsManager


LOGGER = logging.getLogger(__name__)


class AppWindow(Protocol):
    def show_error(self, message: str) -> None:
        ...


class AppController(QObject):
    status_changed = pyqtSignal(str)
    recording_changed = pyqtSignal(bool)
    transcription_updated = pyqtSignal(str)
    level_changed = pyqtSignal(float)
    error = pyqtSignal(str)

    def __init__(self, settings_manager: SettingsManager) -> None:
        super().__init__()
        self.settings_manager = settings_manager
        self.history = HistoryService()
        self.hotkeys = HotkeyService()
        self.startup = StartupService()
        self.typing = TypingService()
        self.windows = WindowService()
        self.text_processor = TextProcessor()
        self.ai = AIService()
        self.recorder: AudioRecorder | None = None
        self.worker = TranscriptionWorker(settings_manager.settings)
        self.window: AppWindow | None = None
        self._wake_until = 0.0

        self.worker.transcription_ready.connect(self._handle_transcription)
        self.worker.status_changed.connect(self.status_changed.emit)
        self.worker.error.connect(self._handle_error)
        self.hotkeys.start_requested.connect(self.start_listening)
        self.hotkeys.stop_requested.connect(self.stop_listening)
        self.hotkeys.error.connect(self._handle_error)
        self.hotkeys.register()
        self.status_changed.emit("Ready")

    def attach_window(self, window: AppWindow) -> None:
        self.window = window

    def apply_settings(self) -> None:
        settings = self.settings_manager.settings
        self.worker.update_settings(settings)
        self.startup.set_enabled(settings.startup_on_windows)

    def start_listening(self) -> None:
        if self.recorder and self.recorder.isRunning():
            return
        settings = self.settings_manager.settings
        self.worker.update_settings(settings)
        if not self.worker.isRunning():
            self.worker.start()

        self.recorder = AudioRecorder(settings)
        self.recorder.audio_ready.connect(self.worker.submit)
        self.recorder.level_changed.connect(self.level_changed.emit)
        self.recorder.status_changed.connect(self.status_changed.emit)
        self.recorder.error.connect(self._handle_error)
        self.recorder.finished.connect(lambda: self.recording_changed.emit(False))
        self.recorder.start()
        self.recording_changed.emit(True)

    def stop_listening(self) -> None:
        if self.recorder and self.recorder.isRunning():
            self.recorder.stop()
            self.recorder.finished.connect(self._recorder_stopped)
        self.recording_changed.emit(False)
        self.status_changed.emit("Ready")

    def _recorder_stopped(self) -> None:
        sender = self.sender()
        if sender and self.recorder is sender:
            self.recorder.deleteLater()
            self.recorder = None

    def shutdown(self) -> None:
        self.hotkeys.unregister()
        self._shutdown_phase()

    def _shutdown_phase(self) -> None:
        if self.recorder and self.recorder.isRunning():
            self.recorder.stop()
            self.recorder.finished.connect(self._shutdown_recorder_done)
            QTimer.singleShot(3000, self._force_quit)
            return
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.finished.connect(self._shutdown_worker_done)
            QTimer.singleShot(3000, self._force_quit)
            return
        QApplication.quit()

    def _shutdown_recorder_done(self) -> None:
        sender = self.sender()
        if sender and self.recorder is sender:
            self.recorder.deleteLater()
            self.recorder = None
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.finished.connect(self._shutdown_worker_done)
        else:
            QApplication.quit()

    def _shutdown_worker_done(self) -> None:
        self.worker = None
        QApplication.quit()

    def _force_quit(self) -> None:
        if self.recorder and self.recorder.isRunning():
            self.recorder.terminate()
            self.recorder.wait(500)
            self.recorder = None
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait(500)
            self.worker = None
        QApplication.quit()

    def _handle_transcription(self, raw_text: str, language: str) -> None:
        settings = self.settings_manager.settings
        raw_text = raw_text.strip()
        if not raw_text:
            return

        candidate = self._apply_wake_word(raw_text)
        if candidate is None:
            self.transcription_updated.emit(raw_text)
            return

        if settings.ai_mode:
            processed = self.ai.process(candidate)
        else:
            processed = self.text_processor.process(candidate, settings.auto_punctuation)

        self.transcription_updated.emit(processed)
        target_window = self.windows.active_window_title()

        if settings.cursor_mode:
            self.windows.focus_cursor()
            target_window = self.windows.active_window_title()

        typed = self.typing.type_text(processed, settings.type_interval, settings.append_space)
        if typed:
            mode = "ai" if settings.ai_mode else "normal"
            if settings.cursor_mode:
                mode = f"{mode}+cursor"
            self.history.add(processed, mode, language, target_window)

    def _apply_wake_word(self, text: str) -> str | None:
        settings = self.settings_manager.settings
        if not settings.wake_word_enabled:
            return text

        now = time.monotonic()
        if self.text_processor.contains_wake_word(text, settings.wake_word):
            self._wake_until = now + 10
            remaining = self.text_processor.remove_wake_word(text, settings.wake_word)
            if remaining:
                return remaining
            self.status_changed.emit("Wake word heard")
            return None

        if now <= self._wake_until:
            self._wake_until = now + 10
            return text

        self.status_changed.emit("Waiting for wake word")
        return None

    def _handle_error(self, message: str) -> None:
        LOGGER.error(message)
        self.error.emit(message)
        if self.window:
            self.window.show_error(message)
