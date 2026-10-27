"""Creeping shadow entity / screen crawler anomaly."""

import math
import random
from typing import Optional, Tuple
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QBrush
from .base import BaseEffect


class ScreenCrawlerEffect(BaseEffect):
    """Shadowy multi-legged critter that skitters along edges."""

    def __init__(
        self,
        start_x: float,
        start_y: float,
        target_edge: str = "right",  # "top", "bottom", "left", "right"
        bounds: Optional[Tuple[int, int, int, int]] = None,
        duration: float = 6.5,
    ):
        super().__init__(duration=duration)
        self.x = start_x
        self.y = start_y
        self.target_edge = target_edge
        self.bounds = bounds
        self.body_size = random.uniform(14.0, 22.0)
        self.speed = random.uniform(160.0, 280.0)
        self.leg_count = 8
        self.walk_cycle = 0.0

        # Crawl direction
        if target_edge == "right":
            self.vx, self.vy = self.speed, random.uniform(-40.0, 40.0)
        elif target_edge == "left":
            self.vx, self.vy = -self.speed, random.uniform(-40.0, 40.0)
        elif target_edge == "bottom":
            self.vx, self.vy = random.uniform(-40.0, 40.0), self.speed
        else:
            self.vx, self.vy = random.uniform(-40.0, 40.0), -self.speed

    def tick(self, dt: float) -> bool:
        if not super().tick(dt):
            return False

        # Periodic erratic twitch
        if random.random() < 0.08:
            self.vx += random.uniform(-30, 30)
            self.vy += random.uniform(-30, 30)

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.walk_cycle += dt * 14.0
        return True

    def render(self, painter: QPainter, width: int, height: int) -> None:
        if not self.is_alive:
            return

        # Alpha fade in and out
        if self.age < 0.6:
            alpha = int(210 * (self.age / 0.6))
        elif self.age > (self.duration - 1.0):
            alpha = int(210 * max(0.0, (self.duration - self.age) / 1.0))
        else:
            alpha = 210

        # Draw articulated shadowy legs
        heading = math.atan2(self.vy, self.vx)
        leg_pen = QPen(QColor(15, 15, 20, int(alpha * 0.85)))
        leg_pen.setWidthF(2.2)
        painter.setPen(leg_pen)

        for i in range(self.leg_count):
            side = 1 if i % 2 == 0 else -1
            leg_idx = i // 2
            leg_phase = self.walk_cycle + (i * 0.7)
            step_ext = math.sin(leg_phase) * 12.0

            angle = heading + (side * (math.pi / 2.8 + (leg_idx * 0.2)))
            reach = self.body_size * 1.8 + step_ext

            # Joint position (knee)
            knee_x = self.x + math.cos(angle) * (reach * 0.6)
            knee_y = self.y + math.sin(angle) * (reach * 0.6) - (math.cos(leg_phase) * 6.0)

            # Tip position (foot)
            foot_x = self.x + math.cos(angle + side * 0.3) * reach
            foot_y = self.y + math.sin(angle + side * 0.3) * reach

            painter.drawLine(QPointF(self.x, self.y), QPointF(knee_x, knee_y))
            painter.drawLine(QPointF(knee_x, knee_y), QPointF(foot_x, foot_y))

        # Draw shadowy core body with pulsing dark aura
        grad = QRadialGradient(QPointF(self.x, self.y), self.body_size * 1.4)
        grad.setColorAt(0.0, QColor(5, 5, 8, alpha))
        grad.setColorAt(0.6, QColor(15, 10, 25, int(alpha * 0.7)))
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(
            QPointF(self.x, self.y),
            self.body_size,
            self.body_size * 0.85
        )

        # Tiny faint eerie eye points
        eye_color = QColor(180, 20, 20, int(alpha * 0.9))
        painter.setBrush(QBrush(eye_color))
        eye_offset = self.body_size * 0.3
        painter.drawEllipse(
            QPointF(self.x + math.cos(heading + 0.35) * eye_offset, self.y + math.sin(heading + 0.35) * eye_offset),
            1.8, 1.8
        )
        painter.drawEllipse(
            QPointF(self.x + math.cos(heading - 0.35) * eye_offset, self.y + math.sin(heading - 0.35) * eye_offset),
            1.8, 1.8
        )

