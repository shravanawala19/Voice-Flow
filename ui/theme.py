from __future__ import annotations

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication


def apply_dark_theme(app: QApplication) -> None:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#101216"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#f5f7fb"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#171b22"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#202632"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#202632"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#f5f7fb"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#f5f7fb"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#202632"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#f5f7fb"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2fd1c5"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#071012"))
    app.setPalette(palette)
    app.setStyleSheet(
        """
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
            color: #f5f7fb;
        }
        QMainWindow, QDialog {
            background: #101216;
        }
        QLabel#Title {
            font-size: 26px;
            font-weight: 700;
            letter-spacing: 0px;
        }
        QLabel#Subtitle {
            color: #9aa7b8;
            font-size: 13px;
        }
        QFrame#Panel {
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 18px;
        }
        QPushButton {
            background: #242b37;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 10px 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #2d3543;
        }
        QPushButton:pressed {
            background: #1d2430;
        }
        QPushButton#PrimaryButton {
            background: #2fd1c5;
            color: #071012;
        }
        QPushButton#DangerButton {
            background: #f25f5c;
            color: #160606;
        }
        QTextEdit, QComboBox, QLineEdit, QDoubleSpinBox {
            background: #171b22;
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 10px;
            padding: 8px;
            selection-background-color: #2fd1c5;
            selection-color: #071012;
        }
        QCheckBox {
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 5px;
            border: 1px solid #5f6b7a;
            background: #171b22;
        }
        QCheckBox::indicator:checked {
            background: #2fd1c5;
            border-color: #2fd1c5;
        }
        QDialogButtonBox QPushButton {
            min-width: 88px;
        }
        """
    )
