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
    assert len(canvas.effects) == 1

    # Crawler spawns a swarm (main + 1-2 companions), so count rises by 2-3
    canvas.spawn_crawler(swarm=False)
    assert len(canvas.effects) == 2

    canvas.spawn_glitch()
    assert len(canvas.effects) == 3

    # Test clear
    canvas.clear_all()
    assert len(canvas.effects) == 0

    # Test swarm spawning produces multiple crawlers
    canvas.spawn_crawler(swarm=True)
    assert len(canvas.effects) >= 2  # main + at least 1 companion

