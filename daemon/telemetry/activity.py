"""User presence and activity sensor."""

import sys
import time
from enum import Enum
from pydantic import BaseModel

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.UINT),
            ("dwTime", wintypes.DWORD),
        ]
else:
    user32 = None
    kernel32 = None


class AttentionState(str, Enum):
    ACTIVE = "active"          # User actively typing / clicking
    DRIFTING = "drifting"      # User paused briefly (5-15s)
    IDLE = "idle"              # User idle (15-60s) - prime haunting zone
    ABSENT = "absent"          # User absent (> 60s)


class ActivityMetrics(BaseModel):
    idle_seconds: float = 0.0
    attention_state: AttentionState = AttentionState.ACTIVE
    cursor_position: tuple[int, int] = (0, 0)


class ActivitySensor:
    def __init__(self, idle_threshold: float = 15.0):
        self.idle_threshold = idle_threshold
        self._last_cursor = (0, 0)

    def read(self) -> ActivityMetrics:
        idle_sec = 0.0
        cursor_pos = (0, 0)

        if sys.platform == "win32" and user32 is not None:
            try:
                # Idle time via GetLastInputInfo
                lii = LASTINPUTINFO()
                lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
                if user32.GetLastInputInfo(ctypes.byref(lii)):
                    millis = kernel32.GetTickCount() - lii.dwTime
                    idle_sec = max(0.0, millis / 1000.0)

                # Cursor position
                class POINT(ctypes.Structure):
                    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]
                pt = POINT()
                if user32.GetCursorPos(ctypes.byref(pt)):
                    cursor_pos = (pt.x, pt.y)
            except Exception:
                pass
        else:
            idle_sec = 0.0

        # Determine attention state
        if idle_sec < 5.0:
            state = AttentionState.ACTIVE
        elif idle_sec < self.idle_threshold:
            state = AttentionState.DRIFTING
        elif idle_sec < 60.0:
            state = AttentionState.IDLE
        else:
            state = AttentionState.ABSENT

        return ActivityMetrics(
            idle_seconds=round(idle_sec, 2),
            attention_state=state,
            cursor_position=cursor_pos,
        )

