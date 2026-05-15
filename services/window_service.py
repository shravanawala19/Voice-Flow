from __future__ import annotations

import logging
import time

try:
    import pygetwindow as gw
    import win32gui
except Exception:  # pragma: no cover - Windows-only optional imports
    gw = None
    win32gui = None


LOGGER = logging.getLogger(__name__)


class WindowService:
    def active_window_title(self) -> str:
        try:
            if win32gui:
                handle = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(handle) or "Unknown"
            if gw:
                active = gw.getActiveWindow()
                return active.title if active else "Unknown"
        except Exception:
            LOGGER.exception("Unable to get active window title")
        return "Unknown"

    def focus_cursor(self) -> bool:
        if gw is None:
            return False
        try:
            windows = [
                window
                for window in gw.getAllWindows()
                if window.title and "cursor" in window.title.lower()
            ]
            if not windows:
                return False
            window = windows[0]
            if window.isMinimized:
                window.restore()
            window.activate()
            time.sleep(0.2)
            return True
        except Exception:
            LOGGER.exception("Unable to focus Cursor")
            return False
