"""Creeping shadow entity / screen crawler anomaly.

Renders an organic, multi-legged shadowy horror entity that skitters
visibly across the desktop with articulated arachnid kinematics.
"""

import math
import random
from typing import Optional, Tuple, List
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QBrush
from .base import BaseEffect


class ScreenCrawlerEffect(BaseEffect):
    """Large, articulated shadow crawler that scuttles across the screen."""

    def __init__(
        self,
        start_x: float,
        start_y: float,
        target_edge: str = "right",
        bounds: Optional[Tuple[int, int, int, int]] = None,
        duration: float = 7.5,
        body_scale: float = 1.0,
    ):
        super().__init__(duration=duration)
        self.x = start_x
        self.y = start_y
        self.target_edge = target_edge
        self.bounds = bounds
        self.body_size = random.uniform(26.0, 38.0) * body_scale
        self.base_speed = random.uniform(220.0, 360.0)
        self.leg_count = 8
        self.walk_cycle = 0.0

        # Motion direction: ensure it scuttles INWARD across the desktop!
        if target_edge == "left":
            # Entered from left edge -> move RIGHTWARD across screen
            self.target_vx = self.base_speed
            self.target_vy = random.uniform(-80.0, 80.0)
        elif target_edge == "right":
            # Entered from right edge -> move LEFTWARD across screen
            self.target_vx = -self.base_speed
            self.target_vy = random.uniform(-80.0, 80.0)
        elif target_edge == "top":
            # Entered from top edge -> move DOWNWARD across screen
            self.target_vx = random.uniform(-80.0, 80.0)
            self.target_vy = self.base_speed
        elif target_edge == "bottom":
            # Entered from bottom edge -> move UPWARD across screen
            self.target_vx = random.uniform(-80.0, 80.0)
            self.target_vy = -self.base_speed
        else:
            # Traversal diagonal across screen
            ang = random.uniform(0, 2 * math.pi)
            self.target_vx = math.cos(ang) * self.base_speed
            self.target_vy = math.sin(ang) * self.base_speed

        self.vx = self.target_vx
        self.vy = self.target_vy

        # Scurry behavior: burst sprint, brief pause, sprint
        self._pause_timer = 0.0
        self._is_paused = False

    def tick(self, dt: float) -> bool:
        if not super().tick(dt):
            return False

        # Periodic predatory pause & twitch behavior
        self._pause_timer += dt
        if not self._is_paused and self._pause_timer > random.uniform(1.2, 2.2):
            self._is_paused = True
            self._pause_timer = 0.0
        elif self._is_paused and self._pause_timer > random.uniform(0.2, 0.45):
            self._is_paused = False
            self._pause_timer = 0.0
            # Sudden velocity surge or directional twitch
            self.vx = self.target_vx * random.uniform(1.1, 1.4) + random.uniform(-40, 40)
            self.vy = self.target_vy * random.uniform(1.1, 1.4) + random.uniform(-40, 40)

        # Apply motion
        if not self._is_paused:
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.walk_cycle += dt * 22.0  # Rapid scuttling steps
        else:
            # Subtle jitter when paused
            self.walk_cycle += dt * 4.0

        return True

    def render(self, painter: QPainter, width: int, height: int) -> None:
        if not self.is_alive:
            return

        # Alpha envelope: smooth fade in (0.4s) and fade out (1.2s)
        fade_in = 0.4
        fade_out = 1.2
        if self.age < fade_in:
            alpha = int(245 * (self.age / fade_in))
        elif self.age > (self.duration - fade_out):
            rem = max(0.0, self.duration - self.age)
            alpha = int(245 * (rem / fade_out))
        else:
            alpha = 245

        heading = math.atan2(self.vy, self.vx)

        # 1. SPECTRAL SHADOW AURA (High-contrast glow visible on both dark & light backgrounds)
        aura_rad = self.body_size * 3.2
        aura = QRadialGradient(QPointF(self.x, self.y), aura_rad)
        aura.setColorAt(0.0, QColor(0, 0, 0, int(alpha * 0.95)))
        aura.setColorAt(0.4, QColor(25, 10, 40, int(alpha * 0.75)))
        aura.setColorAt(0.75, QColor(80, 20, 100, int(alpha * 0.35)))
        aura.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(aura))
        painter.drawEllipse(QPointF(self.x, self.y), aura_rad, aura_rad * 0.9)

        # 2. ARTICULATED JOINTED LEGS
        leg_pen = QPen(QColor(15, 12, 25, alpha))
        leg_pen.setWidthF(3.2)
        leg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(leg_pen)

        for i in range(self.leg_count):
            side = 1 if i % 2 == 0 else -1
            leg_idx = i // 2  # 0, 1, 2, 3 (front to back)
            leg_phase = self.walk_cycle + (i * 0.85)

            # Stepping height & extension kinematics
            step_ext = math.sin(leg_phase) * 16.0
            lift = max(0.0, math.cos(leg_phase)) * 12.0

            # Base joint angle along body flank
            spread = (leg_idx - 1.5) * 0.32
            base_angle = heading + (side * (math.pi / 2.3 + spread))
            reach = self.body_size * 2.4 + step_ext

            # Hip position on body edge
            hip_x = self.x + math.cos(heading + side * 0.8) * (self.body_size * 0.5)
            hip_y = self.y + math.sin(heading + side * 0.8) * (self.body_size * 0.5)

            # Knee (high arched joint)
            knee_angle = base_angle + (side * 0.25)
            knee_dist = reach * 0.65
            knee_x = hip_x + math.cos(knee_angle) * knee_dist
            knee_y = hip_y + math.sin(knee_angle) * knee_dist - lift

            # Foot / claw tip
            foot_angle = base_angle - (side * 0.15)
            foot_x = hip_x + math.cos(foot_angle) * reach
            foot_y = hip_y + math.sin(foot_angle) * reach

            # Draw coxa to knee (upper leg)
            painter.drawLine(QPointF(hip_x, hip_y), QPointF(knee_x, knee_y))
            # Draw knee to claw tip (lower leg)
            painter.drawLine(QPointF(knee_x, knee_y), QPointF(foot_x, foot_y))

            # Knee joint highlight
            painter.setBrush(QBrush(QColor(80, 20, 60, int(alpha * 0.8))))
            painter.drawEllipse(QPointF(knee_x, knee_y), 2.2, 2.2)

        # 3. CHITINOUS BODY SEGMENTS (Abdomen, Cephalothorax, Head)
        painter.setPen(Qt.NoPen)

        # A. Large swollen abdomen (rear)
        ab_dist = -self.body_size * 0.65
        ab_x = self.x + math.cos(heading) * ab_dist
        ab_y = self.y + math.sin(heading) * ab_dist
        ab_grad = QRadialGradient(QPointF(ab_x, ab_y), self.body_size * 0.95)
        ab_grad.setColorAt(0.0, QColor(35, 10, 45, alpha))
        ab_grad.setColorAt(0.6, QColor(10, 8, 18, alpha))
        ab_grad.setColorAt(1.0, QColor(0, 0, 0, alpha))
        painter.setBrush(QBrush(ab_grad))
        painter.drawEllipse(QPointF(ab_x, ab_y), self.body_size * 0.9, self.body_size * 0.75)

        # B. Central Cephalothorax (core)
        core_grad = QRadialGradient(QPointF(self.x, self.y), self.body_size * 0.65)
        core_grad.setColorAt(0.0, QColor(45, 15, 30, alpha))
        core_grad.setColorAt(0.7, QColor(12, 10, 18, alpha))
        core_grad.setColorAt(1.0, QColor(0, 0, 0, alpha))
        painter.setBrush(QBrush(core_grad))
        painter.drawEllipse(QPointF(self.x, self.y), self.body_size * 0.65, self.body_size * 0.55)

        # C. Mandibles / Pincers (front)
        front_x = self.x + math.cos(heading) * (self.body_size * 0.6)
        front_y = self.y + math.sin(heading) * (self.body_size * 0.6)
        pincer_pen = QPen(QColor(30, 10, 25, alpha))
        pincer_pen.setWidthF(2.5)
        painter.setPen(pincer_pen)
        for side in (-1, 1):
            p1_x = front_x + math.cos(heading + side * 0.4) * 8.0
            p1_y = front_y + math.sin(heading + side * 0.4) * 8.0
            p2_x = p1_x + math.cos(heading + side * 0.15) * 14.0
            p2_y = p1_y + math.sin(heading + side * 0.15) * 14.0
            painter.drawLine(QPointF(front_x, front_y), QPointF(p1_x, p1_y))
            painter.drawLine(QPointF(p1_x, p1_y), QPointF(p2_x, p2_y))

        # 4. GLOWING CRIMSON & AMBER ARACHNID EYE CLUSTER
        # 6 glowing predatory eyes at the head
        eye_positions = [
            (0.55, 0.18, 3.0, QColor(255, 40, 60, alpha)),    # Main front left
            (0.55, -0.18, 3.0, QColor(255, 40, 60, alpha)),   # Main front right
            (0.42, 0.32, 2.2, QColor(255, 120, 20, alpha)),   # Lateral left
            (0.42, -0.32, 2.2, QColor(255, 120, 20, alpha)),  # Lateral right
            (0.35, 0.12, 1.8, QColor(255, 0, 40, alpha)),     # Center top left
            (0.35, -0.12, 1.8, QColor(255, 0, 40, alpha)),    # Center top right
        ]

        painter.setPen(Qt.NoPen)
        for forward_ratio, side_angle, rad, eye_col in eye_positions:
            ex = self.x + math.cos(heading + side_angle) * (self.body_size * forward_ratio)
            ey = self.y + math.sin(heading + side_angle) * (self.body_size * forward_ratio)

            # Eye flare glow
            eye_glow = QRadialGradient(QPointF(ex, ey), rad * 2.2)
            eye_glow.setColorAt(0.0, eye_col)
            eye_glow.setColorAt(0.5, QColor(eye_col.red(), eye_col.green(), eye_col.blue(), int(alpha * 0.5)))
            eye_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(eye_glow))
            painter.drawEllipse(QPointF(ex, ey), rad * 2.2, rad * 2.2)

            # Hot white core
            painter.setBrush(QBrush(QColor(255, 230, 240, alpha)))
            painter.drawEllipse(QPointF(ex, ey), rad * 0.6, rad * 0.6)
