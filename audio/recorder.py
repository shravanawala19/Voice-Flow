from __future__ import annotations

import logging
import queue
import time

import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QThread, pyqtSignal

from settings.settings_manager import AppSettings


LOGGER = logging.getLogger(__name__)


class AudioRecorder(QThread):
    audio_ready = pyqtSignal(object)
    level_changed = pyqtSignal(float)
    error = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self._running = False
        self._queue: queue.Queue[np.ndarray] = queue.Queue()

    @staticmethod
    def devices() -> list[dict[str, object]]:
        try:
            devices = sd.query_devices()
            return [
                {"index": idx, "name": device["name"], "channels": device["max_input_channels"]}
                for idx, device in enumerate(devices)
                if int(device["max_input_channels"]) > 0
            ]
        except Exception:
            LOGGER.exception("Unable to query audio devices")
            return []

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        self._running = True
        self.status_changed.emit("Listening")
        block_size = int(self.settings.sample_rate * 0.1)
        try:
            with sd.InputStream(
                samplerate=self.settings.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=block_size,
                device=self.settings.input_device,
                callback=self._callback,
            ):
                self._consume_audio()
        except Exception as exc:
            LOGGER.exception("Microphone capture failed")
            self.error.emit(f"Microphone capture failed: {exc}")
        finally:
            self.status_changed.emit("Stopped")
            self._running = False

    def _callback(self, indata: np.ndarray, frames: int, time_info: object, status: object) -> None:
        if status:
            LOGGER.debug("sounddevice status: %s", status)
        mono = indata[:, 0].copy()
        self._queue.put(mono)
        rms = float(np.sqrt(np.mean(np.square(mono))) if mono.size else 0.0)
        self.level_changed.emit(min(1.0, rms * 18.0))

    def _consume_audio(self) -> None:
        chunks: list[np.ndarray] = []
        speech_started_at: float | None = None
        last_voice_at = time.monotonic()
        max_samples = int(self.settings.chunk_seconds * self.settings.sample_rate)
        min_samples = int(self.settings.min_speech_seconds * self.settings.sample_rate)

        while self._running:
            try:
                block = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue

            chunks.append(block)
            joined = np.concatenate(chunks) if chunks else np.array([], dtype=np.float32)
            if self._is_voice(block):
                if speech_started_at is None:
                    speech_started_at = time.monotonic()
                last_voice_at = time.monotonic()

            enough_speech = joined.size >= min_samples and speech_started_at is not None
            silence_elapsed = time.monotonic() - last_voice_at
            too_long = joined.size >= max_samples
            if enough_speech and (silence_elapsed >= self.settings.silence_timeout_seconds or too_long):
                audio = self._prepare_audio(joined)
                if audio.size:
                    self.audio_ready.emit(audio)
                chunks = []
                speech_started_at = None
                last_voice_at = time.monotonic()

    def _is_voice(self, block: np.ndarray) -> bool:
        if not block.size:
            return False
        rms = float(np.sqrt(np.mean(np.square(block))))
        peak = float(np.max(np.abs(block)))
        return rms > 0.012 or peak > 0.06

    def _prepare_audio(self, audio: np.ndarray) -> np.ndarray:
        audio = audio.astype(np.float32)
        if self.settings.noise_reduction and audio.size:
            return self._noise_gate(audio)
        return audio

    def _noise_gate(self, audio: np.ndarray) -> np.ndarray:
        noise_floor = float(np.percentile(np.abs(audio), 35))
        threshold = max(0.008, noise_floor * 2.2)
        cleaned = audio.copy()
        cleaned[np.abs(cleaned) < threshold] *= 0.25
        peak = float(np.max(np.abs(cleaned))) if cleaned.size else 0.0
        if peak > 0.98:
            cleaned = cleaned / peak * 0.98
        return cleaned.astype(np.float32)
