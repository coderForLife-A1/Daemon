"""Ready-to-run desktop application launcher for Daemon."""

import sys
import signal
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from daemon.config import DaemonConfig
from daemon.ui.dashboard import DaemonDashboard


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Daemon")
    app.setApplicationDisplayName("Daemon: Desktop Poltergeist")

    # Clean Ctrl+C handling in Qt event loop
    signal.signal(signal.SIGINT, lambda *_: QApplication.quit())
    sig_timer = QTimer()
    sig_timer.timeout.connect(lambda: None)
    sig_timer.start(500)

    config = DaemonConfig.load("config.json")
    window = DaemonDashboard(config=config)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

