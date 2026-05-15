from __future__ import annotations

import math

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget


class FloatingMic(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(86, 86)
        self._phase = 0.0
        self._level = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def start(self) -> None:
        self._position()
        self._timer.start(16)
        self.show()

    def stop(self) -> None:
        self._timer.stop()
        self.hide()

    def set_level(self, level: float) -> None:
        self._level = max(0.0, min(1.0, level))

    def _tick(self) -> None:
        self._phase = (self._phase + 0.06) % (math.pi * 2)
        self.update()

    def _position(self) -> None:
        screen = QApplication.primaryScreen()
        if not screen:
            return
        rect = screen.availableGeometry()
        self.move(rect.right() - self.width() - 28, rect.bottom() - self.height() - 28)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pulse = 6 + 10 * self._level + 4 * (math.sin(self._phase) + 1)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(47, 209, 197, 48))
        painter.drawEllipse(8 - pulse / 2, 8 - pulse / 2, 70 + pulse, 70 + pulse)

        painter.setBrush(QColor(18, 21, 27, 220))
        painter.drawEllipse(10, 10, 66, 66)

        painter.setBrush(QColor("#2fd1c5"))
        painter.drawEllipse(20, 20, 46, 46)

        pen = QPen(QColor("#071012"), 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(36, 28, 14, 24, 7, 7)
        painter.drawArc(29, 38, 28, 20, 200 * 16, 140 * 16)
        painter.drawLine(43, 58, 43, 64)
        painter.drawLine(36, 64, 50, 64)
