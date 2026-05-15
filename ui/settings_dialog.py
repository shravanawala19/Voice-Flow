from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QLineEdit,
    QVBoxLayout,
)

from audio.recorder import AudioRecorder
from settings.settings_manager import SettingsManager


class SettingsDialog(QDialog):
    def __init__(self, settings_manager: SettingsManager, parent=None) -> None:
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("VoiceFlow AI Settings")
        self.setMinimumWidth(520)
        self._build()
        self._load_values()

    def values(self) -> dict[str, object]:
        input_device = self.input_device.currentData()
        language = self.language.currentText().strip() or "auto"
        return {
            "model_size": self.model_size.currentText(),
            "model_device": self.model_device.currentText(),
            "compute_type": self.compute_type.currentText(),
            "language": language,
            "input_device": input_device,
            "chunk_seconds": self.chunk_seconds.value(),
            "silence_timeout_seconds": self.silence_timeout.value(),
            "noise_reduction": self.noise_reduction.isChecked(),
            "auto_punctuation": self.auto_punctuation.isChecked(),
            "wake_word_enabled": self.wake_word_enabled.isChecked(),
            "wake_word": self.wake_word.text().strip() or "hey voiceflow",
            "ai_mode": self.ai_mode.isChecked(),
            "cursor_mode": self.cursor_mode.isChecked(),
            "startup_on_windows": self.startup_on_windows.isChecked(),
            "append_space": self.append_space.isChecked(),
        }

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        panel = QFrame()
        panel.setObjectName("Panel")
        form = QFormLayout(panel)
        form.setContentsMargins(18, 18, 18, 18)
        form.setSpacing(12)

        self.model_size = QComboBox()
        self.model_size.addItems(["tiny", "base", "small", "medium", "large-v3"])
        self.model_device = QComboBox()
        self.model_device.addItems(["cpu", "cuda"])
        self.compute_type = QComboBox()
        self.compute_type.addItems(["int8", "float16", "float32"])
        self.language = QComboBox()
        self.language.setEditable(True)
        self.language.addItems(["auto", "en", "es", "fr", "de", "it", "pt", "hi", "zh", "ja", "ko"])

        self.input_device = QComboBox()
        self.input_device.addItem("Default microphone", None)
        for device in AudioRecorder.devices():
            self.input_device.addItem(f"{device['index']} - {device['name']}", device["index"])

        self.chunk_seconds = QDoubleSpinBox()
        self.chunk_seconds.setRange(1.5, 15.0)
        self.chunk_seconds.setSingleStep(0.5)
        self.silence_timeout = QDoubleSpinBox()
        self.silence_timeout.setRange(0.4, 4.0)
        self.silence_timeout.setSingleStep(0.1)

        self.noise_reduction = QCheckBox("Noise reduction")
        self.auto_punctuation = QCheckBox("Auto punctuation")
        self.wake_word_enabled = QCheckBox("Wake word")
        self.wake_word = QLineEdit()
        self.ai_mode = QCheckBox("AI mode")
        self.cursor_mode = QCheckBox("Cursor coding mode")
        self.startup_on_windows = QCheckBox("Start with Windows")
        self.append_space = QCheckBox("Append a space after typing")

        form.addRow("Whisper model", self.model_size)
        form.addRow("Model device", self.model_device)
        form.addRow("Compute type", self.compute_type)
        form.addRow("Language", self.language)
        form.addRow("Microphone", self.input_device)
        form.addRow("Chunk seconds", self.chunk_seconds)
        form.addRow("Silence timeout", self.silence_timeout)
        form.addRow("", self.noise_reduction)
        form.addRow("", self.auto_punctuation)
        form.addRow("", self.wake_word_enabled)
        form.addRow("Wake phrase", self.wake_word)
        form.addRow("", self.ai_mode)
        form.addRow("", self.cursor_mode)
        form.addRow("", self.startup_on_windows)
        form.addRow("", self.append_space)

        layout.addWidget(panel)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons, alignment=Qt.AlignmentFlag.AlignRight)

    def _load_values(self) -> None:
        settings = self.settings_manager.settings
        self._set_combo(self.model_size, settings.model_size)
        self._set_combo(self.model_device, settings.model_device)
        self._set_combo(self.compute_type, settings.compute_type)
        self.language.setCurrentText(settings.language)
        self._set_combo_data(self.input_device, settings.input_device)
        self.chunk_seconds.setValue(settings.chunk_seconds)
        self.silence_timeout.setValue(settings.silence_timeout_seconds)
        self.noise_reduction.setChecked(settings.noise_reduction)
        self.auto_punctuation.setChecked(settings.auto_punctuation)
        self.wake_word_enabled.setChecked(settings.wake_word_enabled)
        self.wake_word.setText(settings.wake_word)
        self.ai_mode.setChecked(settings.ai_mode)
        self.cursor_mode.setChecked(settings.cursor_mode)
        self.startup_on_windows.setChecked(settings.startup_on_windows)
        self.append_space.setChecked(settings.append_space)

    def _set_combo(self, combo: QComboBox, value: str) -> None:
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _set_combo_data(self, combo: QComboBox, value: object) -> None:
        for index in range(combo.count()):
            if combo.itemData(index) == value:
                combo.setCurrentIndex(index)
                return
