from __future__ import annotations

import logging
import sys
from pathlib import Path

try:
    import winreg
except ImportError:  # pragma: no cover
    winreg = None


LOGGER = logging.getLogger(__name__)

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "VoiceFlow AI"


class StartupService:
    def is_enabled(self) -> bool:
        if winreg is None:
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, APP_NAME)
                return True
        except FileNotFoundError:
            return False
        except OSError:
            LOGGER.exception("Unable to read startup registry key")
            return False

    def set_enabled(self, enabled: bool) -> bool:
        if winreg is None:
            return False
        try:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, self._executable_command())
                else:
                    try:
                        winreg.DeleteValue(key, APP_NAME)
                    except FileNotFoundError:
                        pass
            return True
        except OSError:
            LOGGER.exception("Unable to update startup registry key")
            return False

    def _executable_command(self) -> str:
        executable = Path(sys.executable)
        script = Path(sys.argv[0]).resolve()
        if getattr(sys, "frozen", False):
            return f'"{executable}"'
        return f'"{executable}" "{script}"'
