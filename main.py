from __future__ import annotations

import logging
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from services.app_controller import AppController
from settings.settings_manager import SettingsManager
from ui.main_window import MainWindow
from ui.theme import apply_dark_theme


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main() -> int:
    configure_logging()
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("VoiceFlow AI")
    app.setOrganizationName("VoiceFlowAI")
    app.setQuitOnLastWindowClosed(False)
    apply_dark_theme(app)

    settings_manager = SettingsManager()
    controller = AppController(settings_manager)
    window = MainWindow(controller, settings_manager)
    controller.attach_window(window)
    window.show()

    exit_code = app.exec()
    controller.shutdown()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
