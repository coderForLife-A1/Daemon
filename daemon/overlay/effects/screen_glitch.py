"""Screen glitch and full-screen CRT distortion anomaly."""

import math
import random
from typing import List, Tuple
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient
from .base import BaseEffect


class ScreenGlitchEffect(BaseEffect):
    """Full-screen corrupting digital glitch that blankets the display and slowly dissipates."""

    def __init__(self, duration: float = 2.6, intensity: float = 1.0):
        super().__init__(duration=duration)
        self.intensity = intensity
        self._glyph_samples = [
            "0x0000DEAD", "SYS_PANIC", "SIGNAL_LOST", "CORRUPT_SECTOR",
            "01101001", "DAEMON_OVERFLOW", "KERNEL_HIJACK", "NULL_PTR",
            ">> DESYNC <<", "MEMORY_FAULT", "0xFFFF01A", "ERR_STACK"
        ]
        self._frame_count = 0
        self._seed = random.randint(0, 10000)

    def tick(self, dt: float) -> bool:
        self._frame_count += 1
        return super().tick(dt)

    def render(self, painter: QPainter, width: int, height: int) -> None:
        if not self.is_alive:
            return

        progress = min(1.0, max(0.0, self.age / self.duration))

        # Dissolve curve: stays very heavy initially, then breaks apart and dissolves
        # progress 0.0 -> power 1.0
        # Slowly removing: non-linear decay so it stays thick then peels back
        if progress < 0.25:
            # Violent peak initial blackout & static
            coverage = 1.0
            jitter_amp = 1.0
        else:
            # Smoothly recede and break apart
            t = (progress - 0.25) / 0.75
            coverage = max(0.0, (1.0 - t) ** 1.3)
            jitter_amp = max(0.0, 1.0 - t)

        base_alpha = int(235 * coverage * self.intensity)
        if base_alpha <= 0:
            return

        # Deterministic per-frame pseudo-randomness for stability & jitter
        rng = random.Random(self._seed + self._frame_count)

        # 1. FULL SCREEN CORRUPTED VEIL
        # Initially covers the entire screen, then parts from the center outwards
        # creating a tear/fracture revealing the desktop
        veil_alpha = int(base_alpha * (0.85 if progress < 0.3 else 0.75 * (1.0 - progress)))
        if veil_alpha > 0:
            # Glitch background color shifts between void black, deep indigo, and corrupted dark cyan
            tint_select = rng.random()
            if tint_select < 0.15:
                bg_color = QColor(10, 30, 45, veil_alpha)
            elif tint_select < 0.3:
                bg_color = QColor(40, 10, 35, veil_alpha)
            else:
                bg_color = QColor(5, 6, 12, veil_alpha)

            if progress < 0.35:
                # 100% full screen coverage
                painter.fillRect(0, 0, width, height, bg_color)
            else:
                # Fractured reveal: tear horizontal chunks and center open
                tear_open_h = int(height * (progress - 0.35) * 1.5)
                top_h = max(0, (height - tear_open_h) // 2)
                bottom_y = height - top_h

                # Top corrupted slab
                if top_h > 0:
                    painter.fillRect(0, 0, width, top_h, bg_color)
                # Bottom corrupted slab
                if top_h > 0:
                    painter.fillRect(0, bottom_y, width, top_h, bg_color)

                # Random jagged remnant slabs across the middle gap
                for _ in range(int(8 * (1.0 - progress))):
                    slab_y = rng.randint(top_h, max(top_h + 1, bottom_y))
                    slab_h = rng.randint(10, max(12, int(60 * (1.0 - progress))))
                    painter.fillRect(0, slab_y, width, slab_h, bg_color)

        # 2. CHROMATIC ABERRATION & HORIZONTAL DISPLACEMENT SLICES
        # Large full-width tearing slices that shake violently and decay
        slice_count = int(14 * jitter_amp) + 3
        for _ in range(slice_count):
            slice_y = rng.randint(0, max(1, height - 20))
            slice_h = rng.randint(6, int(45 * jitter_amp) + 8)
            shift = int(rng.uniform(-50, 50) * jitter_amp)

            slice_alpha = int(base_alpha * rng.uniform(0.3, 0.7))

            # Cyan split
            painter.fillRect(
                shift, slice_y, width, slice_h,
                QColor(0, 245, 255, int(slice_alpha * 0.45))
            )
            # Magenta / Red split
            painter.fillRect(
                -int(shift * 0.8), slice_y + 2, width, max(1, slice_h - 2),
                QColor(255, 0, 90, int(slice_alpha * 0.40))
            )
            # Dark void fill inside the tear
            if rng.random() < 0.5:
                painter.fillRect(
                    0, slice_y + 1, width, max(1, slice_h // 2),
                    QColor(0, 0, 0, int(slice_alpha * 0.6))
                )

        # 3. DENSE CRT SCANLINES
        # Rapid flickering horizontal raster lines across the whole screen
        scanline_alpha = int(base_alpha * 0.45)
        if scanline_alpha > 0:
            scan_pen = QPen(QColor(0, 0, 0, scanline_alpha))
            scan_pen.setWidth(1)
            painter.setPen(scan_pen)
            step = 3 if progress < 0.4 else 4
            offset = (self._frame_count * 2) % step
            for y in range(offset, height, step):
                if rng.random() < (0.85 if progress < 0.4 else 0.45):
                    painter.drawLine(0, y, width, y)

        # 4. CORRUPTED STATIC DATA BLOCKS / NOISE TILES
        # Scattered noise clusters that dissolve away block by block
        tile_count = int(25 * (1.0 - progress) ** 1.5)
        for _ in range(tile_count):
            tx = rng.randint(0, max(1, width - 150))
            ty = rng.randint(0, max(1, height - 60))
            tw = rng.randint(40, 220)
            th = rng.randint(12, 45)

            # High-contrast static block (bright green, white, or pure black)
            c_type = rng.random()
            if c_type < 0.4:
                tile_color = QColor(255, 255, 255, int(base_alpha * 0.5))
            elif c_type < 0.7:
                tile_color = QColor(0, 255, 160, int(base_alpha * 0.4))
            else:
                tile_color = QColor(0, 0, 0, int(base_alpha * 0.75))

            painter.fillRect(tx, ty, tw, th, tile_color)

        # 5. CREEPING CORRUPTED GLYPHS / BINARY ARTIFACTS
        # Eerie system crash text fragments flashing in the noise
        if progress < 0.7:
            font = QFont("Consolas", 11)
            font.setStyleHint(QFont.Monospace)
            font.setBold(True)
            painter.setFont(font)
            text_alpha = int(base_alpha * 0.8)
            painter.setPen(QColor(200, 255, 220, text_alpha))

            glyph_count = int(6 * (1.0 - progress)) + 1
            for _ in range(glyph_count):
                gx = rng.randint(40, max(50, width - 200))
                gy = rng.randint(30, max(40, height - 40))
                text_sample = rng.choice(self._glyph_samples)
                painter.drawText(QPointF(gx, gy), text_sample)
