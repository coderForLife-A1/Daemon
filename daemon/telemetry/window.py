"""Active foreground window telemetry sensor."""

import os
import sys
from typing import Optional, Tuple
from pydantic import BaseModel
import psutil

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
else:
    user32 = None


class WindowMetrics(BaseModel):
    title: str = "Unknown"
    process_name: str = "Unknown"
    pid: int = 0
    rect: Optional[Tuple[int, int, int, int]] = None  # (left, top, right, bottom)
    is_browser: bool = False
    is_editor: bool = False
    is_terminal: bool = False


class WindowSensor:
    def __init__(self):
        self._last_title = ""
        self._last_process = ""

    def read(self) -> WindowMetrics:
        if sys.platform != "win32" or user32 is None:
            return WindowMetrics(title="Desktop Canvas", process_name="system")

        try:
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return WindowMetrics(title="Desktop", process_name="explorer.exe")

            length = user32.GetWindowTextLengthW(hwnd)
            title = ""
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value

            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            process_pid = pid.value

            process_name = "unknown"
            if process_pid > 0:
                try:
                    proc = psutil.Process(process_pid)
                    process_name = proc.name().lower()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Window rectangle
            rect = None
            try:
                class RECT(ctypes.Structure):
                    _fields_ = [
                        ("left", wintypes.LONG),
                        ("top", wintypes.LONG),
                        ("right", wintypes.LONG),
                        ("bottom", wintypes.LONG),
                    ]
                r = RECT()
                if user32.GetWindowRect(hwnd, ctypes.byref(r)):
                    rect = (r.left, r.top, r.right, r.bottom)
            except Exception:
                pass

            title_lower = title.lower()
            is_browser = any(b in process_name for b in ["chrome", "edge", "firefox", "brave", "opera", "vivaldi"])
            is_editor = any(e in process_name for e in ["code", "cursor", "devenv", "pycharm", "sublime", "notepad", "neovim", "atom"])
            is_terminal = any(t in process_name for t in ["cmd", "powershell", "windowsterminal", "alacritty", "kitty", "bash", "wt"])

            return WindowMetrics(
                title=title if title else (process_name or "Background Activity"),
                process_name=process_name,
                pid=process_pid,
                rect=rect,
                is_browser=is_browser,
                is_editor=is_editor,
                is_terminal=is_terminal,
            )
        except Exception:
            return WindowMetrics(title="Desktop", process_name="explorer.exe")

