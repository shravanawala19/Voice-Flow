from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)


def app_data_dir() -> Path:
    base = os.getenv("APPDATA")
    if base:
        root = Path(base)
    else:
        root = Path.home() / "AppData" / "Roaming"
    path = root / "VoiceFlowAI"
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass(slots=True)
class AppSettings:
    model_size: str = "base"
    model_device: str = "cpu"
    compute_type: str = "int8"
    language: str = "auto"
    input_device: int | None = None
    sample_rate: int = 16000
    chunk_seconds: float = 4.0
    min_speech_seconds: float = 0.55
    silence_timeout_seconds: float = 1.1
    vad_aggressiveness: int = 2
    noise_reduction: bool = True
    auto_punctuation: bool = True
    wake_word_enabled: bool = False
    wake_word: str = "hey voiceflow"
    ai_mode: bool = False
    cursor_mode: bool = False
    startup_on_windows: bool = False
    type_interval: float = 0.01
    append_space: bool = True
    minimize_to_tray: bool = True


class SettingsManager:
    def __init__(self) -> None:
        self.path = app_data_dir() / "settings.json"
        self._settings = self._load()

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def update(self, **values: Any) -> AppSettings:
        data = asdict(self._settings)
        data.update(values)
        self._settings = AppSettings(**self._coerce(data))
        self.save()
        return self._settings

    def save(self) -> None:
        try:
            self.path.write_text(json.dumps(asdict(self._settings), indent=2), encoding="utf-8")
        except OSError:
            LOGGER.exception("Unable to save settings")

    def _load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return AppSettings(**self._coerce(raw))
        except (OSError, json.JSONDecodeError, TypeError):
            LOGGER.exception("Unable to load settings, using defaults")
            return AppSettings()

    @staticmethod
    def _coerce(raw: dict[str, Any]) -> dict[str, Any]:
        defaults = asdict(AppSettings())
        clean = {key: raw.get(key, default) for key, default in defaults.items()}
        if clean["language"] in ("", None):
            clean["language"] = "auto"
        if clean["input_device"] in ("", "None"):
            clean["input_device"] = None
        return clean
