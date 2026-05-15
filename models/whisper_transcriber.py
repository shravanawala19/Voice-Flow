from __future__ import annotations

import logging
import tempfile
import wave
from pathlib import Path

import numpy as np

try:
    from faster_whisper import WhisperModel
except Exception:  # pragma: no cover - import verified at runtime
    WhisperModel = None

from settings.settings_manager import AppSettings


LOGGER = logging.getLogger(__name__)


class FasterWhisperTranscriber:
    def __init__(self) -> None:
        self._model: WhisperModel | None = None
        self._loaded_key: tuple[str, str, str] | None = None

    def transcribe(self, audio: np.ndarray, settings: AppSettings) -> tuple[str, str]:
        if WhisperModel is None:
            raise RuntimeError("faster-whisper is not installed.")
        self._ensure_model(settings)
        if self._model is None:
            return "", settings.language

        wav_path = self._write_temp_wav(audio, settings.sample_rate)
        try:
            language = None if settings.language == "auto" else settings.language
            segments, info = self._model.transcribe(
                str(wav_path),
                language=language,
                vad_filter=True,
                beam_size=5,
                condition_on_previous_text=False,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
            detected_language = getattr(info, "language", settings.language) or settings.language
            return text, detected_language
        finally:
            try:
                wav_path.unlink(missing_ok=True)
            except OSError:
                LOGGER.debug("Unable to remove temp wav", exc_info=True)

    def _ensure_model(self, settings: AppSettings) -> None:
        key = (settings.model_size, settings.model_device, settings.compute_type)
        if self._model is not None and key == self._loaded_key:
            return
        LOGGER.info("Loading Faster-Whisper model: %s", key)
        self._model = WhisperModel(
            settings.model_size,
            device=settings.model_device,
            compute_type=settings.compute_type,
        )
        self._loaded_key = key

    def _write_temp_wav(self, audio: np.ndarray, sample_rate: int) -> Path:
        audio = np.clip(audio, -1.0, 1.0)
        pcm = (audio * 32767).astype(np.int16)
        handle = tempfile.NamedTemporaryFile(prefix="voiceflow_", suffix=".wav", delete=False)
        handle.close()
        path = Path(handle.name)
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm.tobytes())
        return path
