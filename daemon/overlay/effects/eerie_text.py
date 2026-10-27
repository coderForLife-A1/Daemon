"""Floating context-aware eerie text whisper anomaly."""

import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics
from .base import BaseEffect


class EerieTextEffect(BaseEffect):
    """Floating ethereal whisper text with subtle spectral drift and fade."""

    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        duration: float = 7.0,
        font_size: int = 20,
        color: tuple[int, int, int] = (210, 230, 255),
    ):
        super().__init__(duration=duration)
        self.text = text
        self.x = x
        self.y = y
        self.font_size = font_size
        self.base_color = color
        self.drift_vx = random.uniform(-15.0, 15.0)
        self.drift_vy = random.uniform(-10.0, -2.0)
        self.jitter_seed = random.uniform(0, 100)

    def tick(self, dt: float) -> bool:
        if not super().tick(dt):
            return False

        # Gentle drift upwards and sideways
        self.x += self.drift_vx * dt
        self.y += self.drift_vy * dt
        return True

    def render(self, painter: QPainter, width: int, height: int) -> None:
        if not self.is_alive:
            return

        # Alpha envelope: smooth fade in (1.5s), hold, smooth fade out (2.0s)
        fade_in = 1.5
        fade_out = 2.0
        if self.age < fade_in:
            alpha = int(220 * (self.age / fade_in))
        elif self.age > (self.duration - fade_out):
            rem = max(0.0, self.duration - self.age)
            alpha = int(220 * (rem / fade_out))
        else:
            alpha = 220

        # Subtle breathing jitter
        wave = math.sin((self.age + self.jitter_seed) * 3.0) * 2.0
        jitter_x = math.sin((self.age + self.jitter_seed) * 7.0) * 1.5

        # Font configuration
        font = QFont("Consolas", self.font_size)
        font.setStyleHint(QFont.Monospace)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        painter.setFont(font)

        # Draw soft spectral glow behind the text
        glow_color = QColor(60, 15, 90, max(0, int(alpha * 0.45)))
        painter.setPen(glow_color)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
            painter.drawText(
                QPointF(self.x + dx + jitter_x, self.y + dy + wave),
                self.text
            )

        # Draw primary ghostly text
        r, g, b = self.base_color
        text_color = QColor(r, g, b, alpha)
        painter.setPen(text_color)
        painter.drawText(
            QPointF(self.x + jitter_x, self.y + wave),
            self.text
        )

