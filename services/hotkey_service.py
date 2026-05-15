from __future__ import annotations

import logging

from PyQt6.QtCore import QObject, pyqtSignal

try:
    import keyboard
except Exception:  # pragma: no cover - depends on host permissions
    keyboard = None


LOGGER = logging.getLogger(__name__)


class HotkeyService(QObject):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._registered = False

    def register(self) -> None:
        if keyboard is None:
            self.error.emit("Global hotkeys unavailable. Install keyboard or run as administrator.")
            return
        if self._registered:
            return
        try:
            keyboard.add_hotkey("ctrl+shift+v", self.start_requested.emit)
            keyboard.add_hotkey("ctrl+shift+c", self.stop_requested.emit)
            self._registered = True
        except Exception as exc:
            LOGGER.exception("Unable to register global hotkeys")
            self.error.emit(f"Unable to register global hotkeys: {exc}")

    def unregister(self) -> None:
        if keyboard is None or not self._registered:
            return
        try:
            keyboard.remove_hotkey("ctrl+shift+v")
            keyboard.remove_hotkey("ctrl+shift+c")
        except Exception:
            LOGGER.exception("Unable to unregister hotkeys")
        finally:
            self._registered = False
