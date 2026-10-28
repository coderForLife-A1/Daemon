"""Transparent OS Canvas overlay for rendering desktop poltergeist anomalies."""

import sys
import time
import random
from typing import List, Optional
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QGuiApplication, QColor
from PySide6.QtWidgets import QWidget

from .effects import (
    BaseEffect,
    EerieTextEffect,
    ScreenCrawlerEffect,
    ScreenGlitchEffect,
    ShadowWatcherEffect,
)

if sys.platform == "win32":
    import ctypes
    user32 = ctypes.windll.user32
    GWL_EXSTYLE = -20
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_LAYERED = 0x00080000
    WS_EX_TOOLWINDOW = 0x00000080
else:
    user32 = None


class OverlayCanvas(QWidget):
    """Full-desktop transparent overlay with hardware-accelerated QPainter anomalies."""

    def __init__(self, max_entities: int = 5):
        super().__init__()
        self.max_entities = max_entities
        self.effects: List[BaseEffect] = []
        self._last_tick = time.time()

        self._init_window()
        self._setup_timer()

    def _init_window(self) -> None:
        """Configure Qt window attributes for transparent, click-through, non-focus-stealing display."""
        flags = (
            Qt.Window
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput
            | Qt.WindowDoesNotAcceptFocus
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        # Cover combined virtual desktop geometry (multi-monitor support)
        self.update_geometry()

    def update_geometry(self) -> None:
        """Span the virtual geometry of all connected screens."""
        screens = QGuiApplication.screens()
        if screens:
            combined = screens[0].geometry()
            for s in screens[1:]:
                combined = combined.united(s.geometry())
            self.setGeometry(combined)
        else:
            self.setGeometry(0, 0, 1920, 1080)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_native_win32_passthrough()

    def _apply_native_win32_passthrough(self) -> None:
        """Enforce native Windows OS-level mouse click-through transparency."""
        if sys.platform == "win32" and user32 is not None:
            try:
                hwnd = int(self.winId())
                # Retrieve current ex_style
                style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                # Apply WS_EX_TRANSPARENT and WS_EX_LAYERED
                user32.SetWindowLongW(
                    hwnd,
                    GWL_EXSTYLE,
                    style | WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_TOOLWINDOW
                )
            except Exception as e:
                print(f"[Daemon Overlay] Warning: Native win32 click-through setup failed: {e}")

    def _setup_timer(self) -> None:
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_render_tick)
        self.timer.start(33)  # ~30 FPS

    def _on_render_tick(self) -> None:
        now = time.time()
        dt = max(0.001, min(0.1, now - self._last_tick))
        self._last_tick = now

        # Tick effects and prune dead ones
        alive = []
        for e in self.effects:
            if e.tick(dt):
                alive.append(e)
        self.effects = alive

        # Only trigger repaint if there are active effects to draw
        if len(self.effects) > 0:
            self.update()

    def paintEvent(self, event) -> None:
        if not self.effects:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w, h = self.width(), self.height()
        for effect in list(self.effects):
            effect.render(painter, w, h)

    def spawn_whisper(
        self,
        text: str,
        x: Optional[float] = None,
        y: Optional[float] = None,
        duration: float = 7.0
    ) -> None:
        if len(self.effects) >= self.max_entities:
            self.effects.pop(0)

        w, h = self.width(), self.height()
        if x is None:
            x = random.uniform(w * 0.15, w * 0.65)
        if y is None:
            y = random.uniform(h * 0.25, h * 0.75)

        effect = EerieTextEffect(text=text, x=x, y=y, duration=duration)
        self.effects.append(effect)
        self.update()

    def spawn_crawler(
        self,
        target_edge: Optional[str] = None,
        bounds: Optional[tuple] = None,
        duration: float = 6.0
    ) -> None:
        if len(self.effects) >= self.max_entities:
            self.effects.pop(0)

        w, h = self.width(), self.height()
        edges = ["top", "bottom", "left", "right"]
        edge = target_edge or random.choice(edges)

        if edge == "top":
            x, y = random.uniform(50, w - 50), -20
        elif edge == "bottom":
            x, y = random.uniform(50, w - 50), h + 20
        elif edge == "left":
            x, y = -20, random.uniform(50, h - 50)
        else:
            x, y = w + 20, random.uniform(50, h - 50)

        effect = ScreenCrawlerEffect(start_x=x, start_y=y, target_edge=edge, bounds=bounds, duration=duration)
        self.effects.append(effect)
        self.update()

    def spawn_glitch(self, intensity: float = 1.0, duration: float = 2.6) -> None:
        if len(self.effects) >= self.max_entities:
            self.effects.pop(0)

        effect = ScreenGlitchEffect(duration=duration, intensity=intensity)
        self.effects.append(effect)
        self.update()

    def spawn_watcher(self, x: Optional[float] = None, y: Optional[float] = None, duration: float = 8.0) -> None:
        if len(self.effects) >= self.max_entities:
            self.effects.pop(0)

        w, h = self.width(), self.height()
        if x is None or y is None:
            # Pick a corner or edge
            corner = random.choice(["tl", "tr", "bl", "br"])
            if corner == "tl":
                x, y = 90, 80
            elif corner == "tr":
                x, y = w - 90, 80
            elif corner == "bl":
                x, y = 90, h - 80
            else:
                x, y = w - 90, h - 80

        effect = ShadowWatcherEffect(x=x, y=y, duration=duration)
        self.effects.append(effect)
        self.update()

    def clear_all(self) -> None:
        self.effects.clear()
        self.update()

