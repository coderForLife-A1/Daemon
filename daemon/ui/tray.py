"""System Tray interface for Daemon."""

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from ..orchestrator import DaemonOrchestrator


def create_ghost_icon() -> QIcon:
    """Generate a clean procedural 32x32 ghost icon for the tray."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)

    # Ghost body (white/spectral cyan)
    painter.setBrush(QColor(230, 245, 255))
    painter.setPen(Qt.NoPen)
    # Head dome
    painter.drawChord(4, 2, 24, 24, 0, 180 * 16)
    # Body skirt
    painter.drawRect(4, 14, 24, 12)

    # Bottom ripples
    painter.setBrush(Qt.transparent)
    painter.setPen(QColor(230, 245, 255))

    # Eyes
    painter.setBrush(QColor(20, 25, 45))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QPointF(11, 12), 2.5, 3.5)
    painter.drawEllipse(QPointF(21, 12), 2.5, 3.5)

    painter.end()
    return QIcon(pixmap)


class DaemonTrayIcon(QSystemTrayIcon):
    """System tray icon and context menu controller for Daemon."""

    def __init__(self, orchestrator: DaemonOrchestrator, parent=None):
        super().__init__(create_ghost_icon(), parent)
        self.orchestrator = orchestrator
        self.setToolTip("👻 Daemon: AI Desktop Poltergeist")

        self._build_menu()
        self.orchestrator.state_changed.connect(self._on_state_changed)

    def _build_menu(self) -> None:
        menu = QMenu()

        # Status label
        self.status_action = QAction("State: Initializing...", menu)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        menu.addSeparator()

        # Trigger submenu for testing
        test_menu = menu.addMenu("Invoke Anomaly")

        act_whisper = test_menu.addAction("Whisper")
        act_whisper.triggered.connect(lambda: self.orchestrator.trigger_whisper())

        act_crawler = test_menu.addAction("Screen Crawler")
        act_crawler.triggered.connect(lambda: self.orchestrator.trigger_crawler())

        act_glitch = test_menu.addAction("Screen Glitch")
        act_glitch.triggered.connect(lambda: self.orchestrator.trigger_glitch())

        act_watcher = test_menu.addAction("Shadow Watcher")
        act_watcher.triggered.connect(lambda: self.orchestrator.trigger_watcher())

        act_term = test_menu.addAction("Terminal Injection")
        act_term.triggered.connect(lambda: self.orchestrator.trigger_terminal_injection("git status"))

        menu.addSeparator()

        # Pause toggle
        self.pause_action = menu.addAction("Pause Poltergeist")
        self.pause_action.triggered.connect(self._toggle_pause)

        # Audio mute toggle
        self.audio_action = menu.addAction("Mute Audio Synth")
        self.audio_action.setCheckable(True)
        self.audio_action.setChecked(not self.orchestrator.config.enable_audio_synth)
        self.audio_action.triggered.connect(self._toggle_audio)

        menu.addSeparator()

        # Exit
        exit_action = menu.addAction("Banish Daemon (Exit)")
        exit_action.triggered.connect(self._exit_app)

        self.setContextMenu(menu)

    def _toggle_pause(self) -> None:
        is_paused = self.orchestrator.toggle_pause()
        self.pause_action.setText("Resume Poltergeist" if is_paused else "Pause Poltergeist")

    def _toggle_audio(self) -> None:
        muted = self.audio_action.isChecked()
        self.orchestrator.config.enable_audio_synth = not muted
        if self.orchestrator.synth:
            if muted:
                self.orchestrator.synth.stop()
            else:
                self.orchestrator.synth.start()

    def _on_state_changed(self, state: str, tension: float) -> None:
        status_text = f"State: {state.upper()} ({int(tension * 100)}% Tension)"
        self.status_action.setText(status_text)
        self.setToolTip(f"👻 Daemon: {status_text}")

    def _exit_app(self) -> None:
        self.orchestrator.stop()
        QApplication.quit()

