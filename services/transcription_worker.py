from __future__ import annotations

import logging
import queue

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from models.whisper_transcriber import FasterWhisperTranscriber
from settings.settings_manager import AppSettings


LOGGER = logging.getLogger(__name__)


class TranscriptionWorker(QThread):
    transcription_ready = pyqtSignal(str, str)
    status_changed = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self._queue: queue.Queue[np.ndarray | None] = queue.Queue()
        self._running = False
        self._transcriber = FasterWhisperTranscriber()

    def submit(self, audio: np.ndarray) -> None:
        self._queue.put(audio)

    def update_settings(self, settings: AppSettings) -> None:
        self.settings = settings

    def stop(self) -> None:
        self._running = False
        self._queue.put(None)

    def run(self) -> None:
        self._running = True
        while self._running:
            audio = self._queue.get()
            if audio is None:
                break
            try:
                self.status_changed.emit("Transcribing")
                text, language = self._transcriber.transcribe(audio, self.settings)
                self.transcription_ready.emit(text, language)
            except Exception as exc:
                LOGGER.exception("Transcription failed")
                self.error.emit(f"Transcription failed: {exc}")
            finally:
                if self._running:
                    self.status_changed.emit("Listening")
