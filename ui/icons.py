from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


def app_icon(size: int = 64, active: bool = False) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    bg = QColor("#2fd1c5" if active else "#242b37")
    painter.setBrush(bg)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, size - 4, size - 4)

    pen = QPen(QColor("#071012" if active else "#f5f7fb"), max(2, size // 18))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    mic_rect = QRectF(size * 0.36, size * 0.18, size * 0.28, size * 0.42)
    painter.drawRoundedRect(mic_rect, size * 0.13, size * 0.13)
    painter.drawArc(QRectF(size * 0.25, size * 0.36, size * 0.50, size * 0.34), 200 * 16, 140 * 16)
    painter.drawLine(QPointF(size * 0.50, size * 0.72), QPointF(size * 0.50, size * 0.84))
    painter.drawLine(QPointF(size * 0.39, size * 0.84), QPointF(size * 0.61, size * 0.84))

    painter.end()
    return QIcon(pixmap)


def status_dot(color: str, size: int = 16) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addEllipse(2, 2, size - 4, size - 4)
    painter.fillPath(path, QColor(color))
    painter.end()
    return pixmap
