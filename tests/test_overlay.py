"""Unit tests for the visual overlay canvas and effects."""

from PySide6.QtWidgets import QApplication
from daemon.overlay import OverlayCanvas


def test_overlay_canvas_init():
    app = QApplication.instance() or QApplication([])
    canvas = OverlayCanvas(max_entities=3)

    assert canvas.max_entities == 3
    assert len(canvas.effects) == 0

    # Test spawning effects
    canvas.spawn_whisper("The kernel watches.")
    canvas.spawn_crawler()
    canvas.spawn_glitch()
    assert len(canvas.effects) == 3

    # Test overflow pops oldest effect
    canvas.spawn_watcher()
    assert len(canvas.effects) == 3

    # Test clear
    canvas.clear_all()
    assert len(canvas.effects) == 0

