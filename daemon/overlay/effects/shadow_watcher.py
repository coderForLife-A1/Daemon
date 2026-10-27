"""Shadow watcher / peering eyes anomaly."""

import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient
from .base import BaseEffect


class ShadowWatcherEffect(BaseEffect):
    """Pair of ethereal eyes slowly opening in a dark corner to observe."""

    def __init__(self, x: float, y: float, duration: float = 8.0):
        super().__init__(duration=duration)
        self.x = x
        self.y = y
        self.eye_spacing = 38.0
        self.eye_width = 24.0
        self.eye_height = 14.0
        self.glow_color = QColor(190, 220, 255)
        self.pupil_drift = 0.0

    def tick(self, dt: float) -> bool:
        if not super().tick(dt):
            return False
        self.pupil_drift = math.sin(self.age * 2.0) * 4.0
        return True

    def render(self, painter: QPainter, width: int, height: int) -> None:
        if not self.is_alive:
            return

        # Fade in, sustain, fade out
        if self.age < 2.0:
            alpha = int(200 * (self.age / 2.0))
        elif self.age > (self.duration - 2.0):
            alpha = int(200 * max(0.0, (self.duration - self.age) / 2.0))
        else:
            alpha = 200

        # Eyelid blink factor (0 = closed, 1 = fully open)
        open_factor = min(1.0, self.age / 1.5)
        # Occasional blink
        if 4.0 < self.age < 4.25:
            open_factor = 0.1

        h = self.eye_height * open_factor
        if h < 1.0:
            return

        # Ambient shadow vignette behind the eyes
        bg_grad = QRadialGradient(QPointF(self.x, self.y), 110.0)
        bg_grad.setColorAt(0.0, QColor(0, 0, 5, int(alpha * 0.7)))
        bg_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_grad))
        painter.drawEllipse(QPointF(self.x, self.y), 110.0, 70.0)

        # Draw left and right eyes
        for side in (-1, 1):
            ex = self.x + side * (self.eye_spacing / 2.0)
            ey = self.y

            # Outer eye glow
            eye_grad = QRadialGradient(QPointF(ex, ey), self.eye_width * 0.9)
            eye_grad.setColorAt(0.0, QColor(220, 240, 255, alpha))
            eye_grad.setColorAt(0.4, QColor(120, 180, 240, int(alpha * 0.7)))
            eye_grad.setColorAt(1.0, QColor(30, 60, 120, 0))

            painter.setBrush(QBrush(eye_grad))
            painter.drawEllipse(QPointF(ex, ey), self.eye_width / 2.0, h / 2.0)

            # Slit pupil
            pupil_x = ex + self.pupil_drift
            painter.setBrush(QBrush(QColor(5, 5, 10, int(alpha * 0.95))))
            painter.drawEllipse(QPointF(pupil_x, ey), 2.2, h * 0.45)

