"""Screen glitch and CRT distortion anomaly."""

import random
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient
from .base import BaseEffect


class ScreenGlitchEffect(BaseEffect):
    """Brief CRT glitch tear and chromatic static artifact."""

    def __init__(self, duration: float = 0.8, intensity: float = 0.8):
        super().__init__(duration=duration)
        self.intensity = intensity
        self.bands = [
            (random.uniform(0.1, 0.9), random.uniform(8, 35), random.uniform(-40, 40))
            for _ in range(random.randint(3, 7))
        ]

    def render(self, painter: QPainter, width: int, height: int) -> None:
        if not self.is_alive:
            return

        # Fast strobe envelope
        envelope = 1.0 - (self.age / self.duration)
        alpha = int(140 * envelope * self.intensity)

        # 1. Dark vignette pulse around screen borders
        border_grad = QLinearGradient(0, 0, 0, height)
        border_grad.setColorAt(0.0, QColor(0, 0, 0, int(alpha * 0.4)))
        border_grad.setColorAt(0.05, QColor(0, 0, 0, 0))
        border_grad.setColorAt(0.95, QColor(0, 0, 0, 0))
        border_grad.setColorAt(1.0, QColor(0, 0, 0, int(alpha * 0.4)))
        painter.fillRect(0, 0, width, height, QBrush(border_grad))

        # 2. Horizontal tear bands
        for rel_y, band_h, shift in self.bands:
            y = int(rel_y * height)
            # Chromatic cyan/magenta edge bands
            painter.fillRect(
                int(shift), y, width, int(band_h),
                QColor(0, 240, 255, int(alpha * 0.25))
            )
            painter.fillRect(
                int(-shift * 0.7), y + 2, width, int(band_h * 0.8),
                QColor(255, 0, 80, int(alpha * 0.2))
            )
            painter.fillRect(
                0, y + 4, width, int(band_h * 0.5),
                QColor(10, 10, 15, int(alpha * 0.5))
            )

        # 3. Fine scanline raster overlay across tear area
        scanline_pen = QPen(QColor(0, 0, 0, int(alpha * 0.3)))
        scanline_pen.setWidth(1)
        painter.setPen(scanline_pen)
        step = 4
        for y in range(0, height, step):
            if random.random() < 0.25:
                painter.drawLine(0, y, width, y)

