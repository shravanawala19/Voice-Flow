from __future__ import annotations

import logging
import time

import pyautogui
import pyperclip


LOGGER = logging.getLogger(__name__)


class TypingService:
    def __init__(self) -> None:
        pyautogui.FAILSAFE = True

    def type_text(self, text: str, interval: float = 0.01, append_space: bool = True) -> bool:
        if not text.strip():
            return False
        payload = text + (" " if append_space and not text.endswith(("\n", " ")) else "")
        try:
            time.sleep(0.08)
            if payload.isascii() and "\n" not in payload:
                pyautogui.write(payload, interval=interval)
            else:
                self._paste_text(payload)
            return True
        except Exception:
            LOGGER.exception("Unable to type transcription")
            return False

    def press_enter(self) -> None:
        try:
            pyautogui.press("enter")
        except Exception:
            LOGGER.exception("Unable to press Enter")

    def _paste_text(self, text: str) -> None:
        previous = pyperclip.paste()
        try:
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
        finally:
            time.sleep(0.1)
            try:
                pyperclip.copy(previous)
            except Exception:
                pass
