"""Unit tests for Daemon desktop dashboard UI."""

from PySide6.QtWidgets import QApplication
from daemon.config import DaemonConfig
from daemon.ui import DaemonDashboard


def test_dashboard_creation():
    app = QApplication.instance() or QApplication([])
    config = DaemonConfig()
    dashboard = DaemonDashboard(config=config)

    assert dashboard.windowTitle() == "👻 Daemon: Control Hub"
    assert dashboard.orchestrator is None

    # Test starting engine
    dashboard._start_engine()
    assert dashboard.orchestrator is not None
    assert dashboard.canvas is not None
    assert dashboard.btn_toggle_power.text() == "STOP DAEMON"

    # Test manual anomaly invocation buttons without errors
    dashboard._manual_whisper()
    dashboard._manual_crawler()
    dashboard._manual_glitch()
    dashboard._manual_watcher()

    # Test stopping engine
    dashboard._stop_engine()
    assert dashboard.orchestrator is None
    assert dashboard.canvas is None
    assert dashboard.btn_toggle_power.text() == "START DAEMON"

    dashboard.close()

