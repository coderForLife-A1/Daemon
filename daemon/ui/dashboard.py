"""Desktop Control Center UI for Daemon.

A sleek, dark atmospheric desktop application to start, monitor,
configure, and trigger Daemon anomalies with live telemetry visualizations.
"""

import sys
import time
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QLinearGradient, QBrush, QPen
from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QSlider,
    QComboBox,
    QSpinBox,
    QGroupBox,
    QTextEdit,
    QFrame,
    QScrollArea,
    QSplitter,
    QCheckBox,
    QLineEdit,
    QApplication,
)

from ..config import DaemonConfig
from ..orchestrator import DaemonOrchestrator, HauntState
from ..overlay import OverlayCanvas
from ..audio import AudioSynth
from .tray import create_ghost_icon, DaemonTrayIcon


# High-contrast cyber-haunt dark theme stylesheet
STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0d0f17;
    color: #e0e6ed;
    font-family: 'Segoe UI', Consolas, sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #1f2638;
    border-radius: 8px;
    margin-top: 20px;
    font-weight: bold;
    color: #8fa0b8;
    background-color: #121622;
    padding-top: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    background-color: #171d2b;
    border-radius: 4px;
    color: #00e5ff;
}

QLabel {
    color: #c4d1df;
}

QPushButton {
    background-color: #1a2234;
    border: 1px solid #2a3652;
    border-radius: 6px;
    color: #e6edf5;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #243048;
    border-color: #00e5ff;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #151c2a;
}

QPushButton#btn_start {
    background-color: #0c3d2e;
    border: 1px solid #00ff9d;
    color: #00ff9d;
    font-size: 14px;
    font-weight: bold;
    padding: 12px;
}

QPushButton#btn_start:hover {
    background-color: #115741;
}

QPushButton#btn_stop {
    background-color: #401018;
    border: 1px solid #ff3366;
    color: #ff3366;
    font-size: 14px;
    font-weight: bold;
    padding: 12px;
}

QPushButton#btn_stop:hover {
    background-color: #5c1824;
}

QPushButton.anomaly_btn {
    background-color: #161b29;
    border: 1px solid #2b354d;
    padding: 10px;
}

QPushButton.anomaly_btn:hover {
    border-color: #bd93f9;
    background-color: #221c38;
    color: #bd93f9;
}

QProgressBar {
    border: 1px solid #21293c;
    border-radius: 6px;
    background-color: #0a0c13;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    height: 22px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8a2be2, stop:0.7 #ff007f, stop:1 #ff3366);
    border-radius: 5px;
}

QSlider::groove:horizontal {
    border: 1px solid #1f273b;
    height: 6px;
    background: #090b10;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #00e5ff;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #00e5ff;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

QTextEdit {
    background-color: #080a0f;
    border: 1px solid #181f2f;
    border-radius: 6px;
    color: #79f8aa;
    font-family: 'Consolas', monospace;
    font-size: 12px;
    padding: 8px;
}

QComboBox, QSpinBox, QLineEdit {
    background-color: #161d2b;
    border: 1px solid #27344c;
    border-radius: 5px;
    padding: 5px 10px;
    color: #e6edf5;
}

QLineEdit:focus {
    border-color: #00e5ff;
}

QComboBox::drop-down {
    border: none;
}
"""


class DaemonDashboard(QMainWindow):
    """Main desktop control window for Daemon."""

    def __init__(self, config: Optional[DaemonConfig] = None):
        super().__init__()
        self.config = config or DaemonConfig.load("config.json")
        self.setWindowTitle("👻 Daemon: Control Hub")
        self.setWindowIcon(create_ghost_icon())
        self.resize(920, 680)
        self.setStyleSheet(STYLESHEET)

        # Core engine components
        self.canvas: Optional[OverlayCanvas] = None
        self.synth: Optional[AudioSynth] = None
        self.orchestrator: Optional[DaemonOrchestrator] = None
        self.tray: Optional[DaemonTrayIcon] = None

        self._init_ui()
        self._setup_poll_timer()

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- HEADER BANNER ---
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        app_title = QLabel("👻 DAEMON: POLTERGEIST CORE")
        app_title.setFont(QFont("Consolas", 18, QFont.Bold))
        app_title.setStyleSheet("color: #00e5ff; letter-spacing: 2px;")
        sub_title = QLabel("Presence-aware system poltergeist & atmospheric anomaly engine")
        sub_title.setStyleSheet("color: #71849d; font-size: 12px;")
        title_box.addWidget(app_title)
        title_box.addWidget(sub_title)
        header.addLayout(title_box)

        header.addStretch()

        # Engine Power Button
        self.btn_toggle_power = QPushButton("START DAEMON")
        self.btn_toggle_power.setObjectName("btn_start")
        self.btn_toggle_power.setFixedWidth(180)
        self.btn_toggle_power.clicked.connect(self._toggle_engine)
        header.addWidget(self.btn_toggle_power)

        main_layout.addLayout(header)

        # --- SPLIT BODY ---
        splitter = QSplitter(Qt.Horizontal)

        # LEFT COLUMN: Telemetry & State Monitor
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)

        # 1. HAUNT STATE & TENSION
        haunt_group = QGroupBox("PSYCHIC TENSION & STATE")
        hg_layout = QVBoxLayout(haunt_group)

        state_row = QHBoxLayout()
        state_label = QLabel("Entity State:")
        self.lbl_state = QLabel("OFFLINE")
        self.lbl_state.setFont(QFont("Consolas", 13, QFont.Bold))
        self.lbl_state.setStyleSheet("color: #ff3366;")
        state_row.addWidget(state_label)
        state_row.addWidget(self.lbl_state)
        state_row.addStretch()
        hg_layout.addLayout(state_row)

        hg_layout.addWidget(QLabel("Haunting Tension Meter:"))
        self.tension_bar = QProgressBar()
        self.tension_bar.setRange(0, 100)
        self.tension_bar.setValue(0)
        hg_layout.addWidget(self.tension_bar)

        left_layout.addWidget(haunt_group)

        # 2. LIVE SYSTEM TELEMETRY
        telemetry_group = QGroupBox("REAL-TIME TELEMETRY SENSORS")
        tg_layout = QVBoxLayout(telemetry_group)

        self.lbl_cpu = QLabel("CPU Load: --%")
        self.lbl_ram = QLabel("Memory: -- GB / -- GB (--%)")
        self.lbl_window = QLabel("Active Window: --")
        self.lbl_process = QLabel("Foreground Process: --")
        self.lbl_idle = QLabel("User Inactivity: 0.0s")
        self.lbl_attention = QLabel("Attention Level: ACTIVE")

        for lbl in (self.lbl_cpu, self.lbl_ram, self.lbl_window, self.lbl_process, self.lbl_idle, self.lbl_attention):
            lbl.setStyleSheet("font-family: Consolas; color: #a4b8cf;")
            tg_layout.addWidget(lbl)

        left_layout.addWidget(telemetry_group)

        # 3. MANUAL ANOMALY DISPATCH
        trigger_group = QGroupBox("INVOKE ANOMALY (MANUAL OVERRIDE)")
        trig_layout = QVBoxLayout(trigger_group)

        btn_row_1 = QHBoxLayout()
        self.btn_whisper = QPushButton("💬 Context Whisper")
        self.btn_whisper.setProperty("class", "anomaly_btn")
        self.btn_whisper.clicked.connect(self._manual_whisper)
        self.btn_crawler = QPushButton("🕷️ Screen Crawler")
        self.btn_crawler.setProperty("class", "anomaly_btn")
        self.btn_crawler.clicked.connect(self._manual_crawler)
        btn_row_1.addWidget(self.btn_whisper)
        btn_row_1.addWidget(self.btn_crawler)

        btn_row_2 = QHBoxLayout()
        self.btn_glitch = QPushButton("⚡ Full-Screen Glitch")
        self.btn_glitch.setProperty("class", "anomaly_btn")
        self.btn_glitch.clicked.connect(self._manual_glitch)
        self.btn_watcher = QPushButton("👁️ Shadow Watcher")
        self.btn_watcher.setProperty("class", "anomaly_btn")
        self.btn_watcher.clicked.connect(self._manual_watcher)
        btn_row_2.addWidget(self.btn_glitch)
        btn_row_2.addWidget(self.btn_watcher)

        trig_layout.addLayout(btn_row_1)
        trig_layout.addLayout(btn_row_2)

        # Terminal Injection Simulator Row
        term_label = QLabel("Corrupt Terminal Command:")
        term_label.setStyleSheet("color: #71849d; font-size: 11px; margin-top: 6px;")
        trig_layout.addWidget(term_label)

        term_row = QHBoxLayout()
        self.txt_term_cmd = QLineEdit()
        self.txt_term_cmd.setPlaceholderText("e.g. git status, python app.py, ls -la")
        self.txt_term_cmd.setText("git status")
        self.btn_term_inject = QPushButton("📟 Inject")
        self.btn_term_inject.setProperty("class", "anomaly_btn")
        self.btn_term_inject.clicked.connect(self._manual_terminal_injection)
        term_row.addWidget(self.txt_term_cmd)
        term_row.addWidget(self.btn_term_inject)
        trig_layout.addLayout(term_row)

        left_layout.addWidget(trigger_group)
        splitter.addWidget(left_panel)

        # RIGHT COLUMN: Settings & Console Log
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # 1. CONFIGURATION
        config_group = QGroupBox("RUNTIME CONFIGURATION")
        cfg_layout = QVBoxLayout(config_group)

        # Threshold slider
        t_label_row = QHBoxLayout()
        t_label_row.addWidget(QLabel("Anomaly Threshold:"))
        self.lbl_threshold_val = QLabel(f"{int(self.config.anomaly_threshold * 100)}%")
        self.lbl_threshold_val.setStyleSheet("color: #00e5ff; font-weight: bold;")
        t_label_row.addWidget(self.lbl_threshold_val)
        cfg_layout.addLayout(t_label_row)

        self.slider_threshold = QSlider(Qt.Horizontal)
        self.slider_threshold.setRange(10, 100)
        self.slider_threshold.setValue(int(self.config.anomaly_threshold * 100))
        self.slider_threshold.valueChanged.connect(self._on_threshold_changed)
        cfg_layout.addWidget(self.slider_threshold)

        # Sound Volume slider
        v_label_row = QHBoxLayout()
        v_label_row.addWidget(QLabel("Procedural Audio Volume:"))
        self.lbl_volume_val = QLabel(f"{int(self.config.sound_volume * 100)}%")
        self.lbl_volume_val.setStyleSheet("color: #00e5ff; font-weight: bold;")
        v_label_row.addWidget(self.lbl_volume_val)
        cfg_layout.addLayout(v_label_row)

        self.slider_volume = QSlider(Qt.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(int(self.config.sound_volume * 100))
        self.slider_volume.valueChanged.connect(self._on_volume_changed)
        cfg_layout.addWidget(self.slider_volume)

        # Model & Entities
        row_opts = QHBoxLayout()
        row_opts.addWidget(QLabel("Ollama Model:"))
        self.combo_model = QComboBox()
        self.combo_model.addItems(["llama3.2:1b", "qwen2.5:1.5b", "phi3:mini", "mistral:7b"])
        idx = self.combo_model.findText(self.config.model_name)
        if idx >= 0:
            self.combo_model.setCurrentIndex(idx)
        else:
            self.combo_model.addItem(self.config.model_name)
            self.combo_model.setCurrentText(self.config.model_name)
        self.combo_model.currentTextChanged.connect(self._on_model_changed)
        row_opts.addWidget(self.combo_model)

        self.chk_audio = QCheckBox("Enable Audio Synth")
        self.chk_audio.setChecked(self.config.enable_audio_synth)
        self.chk_audio.toggled.connect(self._on_audio_toggled)
        row_opts.addWidget(self.chk_audio)

        cfg_layout.addLayout(row_opts)

        right_layout.addWidget(config_group)

        # 2. ACTIVITY & EVENT LOG
        log_group = QGroupBox("ENTITY EVENT LOG")
        lg_layout = QVBoxLayout(log_group)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        lg_layout.addWidget(self.log_view)

        right_layout.addWidget(log_group)
        splitter.addWidget(right_panel)

        main_layout.addWidget(splitter)

        # Bottom Actions
        bottom_bar = QHBoxLayout()
        self.lbl_status = QLabel("● Ready. Press 'START DAEMON' to release the entity into the background.")
        self.lbl_status.setStyleSheet("color: #8da4be;")
        bottom_bar.addWidget(self.lbl_status)
        bottom_bar.addStretch()

        btn_save = QPushButton("Save Config")
        btn_save.clicked.connect(self._save_config)
        bottom_bar.addWidget(btn_save)

        btn_tray = QPushButton("Send to Tray")
        btn_tray.clicked.connect(self.hide_to_tray)
        bottom_bar.addWidget(btn_tray)

        main_layout.addLayout(bottom_bar)

        self._log_event("Daemon Desktop Hub initialized. Ready to run.")

    def _setup_poll_timer(self) -> None:
        """Poll telemetry and update dashboard metrics."""
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._refresh_metrics)
        self.poll_timer.start(1000)

    def _toggle_engine(self) -> None:
        if self.orchestrator is None:
            self._start_engine()
        else:
            self._stop_engine()

    def _start_engine(self) -> None:
        """Start overlay canvas, audio synth, and orchestrator."""
        try:
            # 1. Overlay Canvas
            self.canvas = OverlayCanvas(max_entities=self.config.max_entities)
            self.canvas.show()

            # 2. Audio Synth
            self.synth = AudioSynth(
                master_volume=self.config.sound_volume,
                enabled=self.config.enable_audio_synth,
            )

            # 3. Orchestrator
            self.orchestrator = DaemonOrchestrator(
                config=self.config,
                canvas=self.canvas,
                synth=self.synth,
            )
            self.orchestrator.state_changed.connect(self._on_orchestrator_state)
            self.orchestrator.anomaly_triggered.connect(self._on_anomaly_triggered)

            # 4. System Tray
            if DaemonTrayIcon.isSystemTrayAvailable() and self.tray is None:
                self.tray = DaemonTrayIcon(orchestrator=self.orchestrator, parent=self)
                self.tray.show()

            self.orchestrator.start()

            self.btn_toggle_power.setText("STOP DAEMON")
            self.btn_toggle_power.setObjectName("btn_stop")
            self.btn_toggle_power.setStyle(self.btn_toggle_power.style())
            self.lbl_status.setText("● Daemon is active in background and monitoring desktop.")
            self._log_event("Daemon engine started successfully. Transparent overlay active.")
        except Exception as e:
            self._log_event(f"Error starting Daemon: {e}")

    def _stop_engine(self) -> None:
        """Halt orchestrator and hide overlay."""
        if self.orchestrator:
            self.orchestrator.stop()
            self.orchestrator = None

        if self.canvas:
            self.canvas.close()
            self.canvas = None

        if self.synth:
            self.synth.stop()
            self.synth = None

        self.btn_toggle_power.setText("START DAEMON")
        self.btn_toggle_power.setObjectName("btn_start")
        self.btn_toggle_power.setStyle(self.btn_toggle_power.style())
        self.lbl_state.setText("OFFLINE")
        self.lbl_state.setStyleSheet("color: #ff3366;")
        self.tension_bar.setValue(0)
        self.lbl_status.setText("● Daemon stopped.")
        self._log_event("Daemon engine stopped.")

    def _refresh_metrics(self) -> None:
        """Update live telemetry metrics on dashboard."""
        if self.orchestrator:
            snap = self.orchestrator.telemetry.capture()
            self.lbl_cpu.setText(f"CPU Load: {snap.system.cpu_percent:.1f}%")
            self.lbl_ram.setText(f"Memory: {snap.system.ram_used_gb:.1f} GB / {snap.system.ram_total_gb:.1f} GB ({snap.system.ram_percent:.0f}%)")
            title = snap.window.title[:45] + "..." if len(snap.window.title) > 45 else snap.window.title
            self.lbl_window.setText(f"Active Window: {title or 'Desktop'}")
            self.lbl_process.setText(f"Foreground Process: {snap.window.process_name}")
            self.lbl_idle.setText(f"User Inactivity: {snap.activity.idle_seconds:.1f}s")
            self.lbl_attention.setText(f"Attention Level: {snap.activity.attention_state.value.upper()}")

    def _on_orchestrator_state(self, state: str, tension: float) -> None:
        state_colors = {
            "dormant": "#00e5ff",
            "observing": "#ffe600",
            "lurking": "#ff8800",
            "haunting": "#ff0055",
            "cooldown": "#9d4edd",
        }
        color = state_colors.get(state.lower(), "#00e5ff")
        self.lbl_state.setText(state.upper())
        self.lbl_state.setStyleSheet(f"color: {color};")
        self.tension_bar.setValue(int(tension * 100))

    def _on_anomaly_triggered(self, kind: str, detail: str) -> None:
        self._log_event(f"ANOMALY DISPATCHED: [{kind.upper()}] - {detail}")

    def _manual_whisper(self) -> None:
        if self.orchestrator:
            whisper = self.orchestrator.trigger_whisper()
            self._log_event(f"Manual whisper invoked: \"{whisper}\"")
        else:
            self._log_event("Start the daemon first to invoke anomalies.")

    def _manual_crawler(self) -> None:
        if self.orchestrator:
            self.orchestrator.trigger_crawler()
            self._log_event("Manual screen crawler released onto perimeter.")
        else:
            self._log_event("Start the daemon first to invoke anomalies.")

    def _manual_glitch(self) -> None:
        if self.orchestrator:
            self.orchestrator.trigger_glitch()
            self._log_event("Manual full-screen glitch triggered.")
        else:
            self._log_event("Start the daemon first to invoke anomalies.")

    def _manual_watcher(self) -> None:
        if self.orchestrator:
            self.orchestrator.trigger_watcher()
            self._log_event("Manual shadow watcher summoned to desktop corner.")
        else:
            self._log_event("Start the daemon first to invoke anomalies.")

    def _manual_terminal_injection(self) -> None:
        cmd = self.txt_term_cmd.text().strip() or "git status"
        if self.orchestrator:
            res = self.orchestrator.trigger_terminal_injection(cmd)
        else:
            from ..terminal import TerminalInterceptor
            interceptor = TerminalInterceptor(model_name=self.config.model_name)
            res = interceptor.corrupt_command(cmd)

        self._log_event(f"Terminal Command: '{cmd}'")
        for line in res.splitlines():
            self._log_event(f"  > {line}")

    def _on_threshold_changed(self, val: int) -> None:
        self.config.anomaly_threshold = val / 100.0
        self.lbl_threshold_val.setText(f"{val}%")
        if self.orchestrator:
            self.orchestrator.state_machine.anomaly_threshold = self.config.anomaly_threshold

    def _on_volume_changed(self, val: int) -> None:
        self.config.sound_volume = val / 100.0
        self.lbl_volume_val.setText(f"{val}%")
        if self.synth:
            self.synth.master_volume = self.config.sound_volume

    def _on_model_changed(self, text: str) -> None:
        self.config.model_name = text
        if self.orchestrator:
            self.orchestrator.ai.model_name = text

    def _on_audio_toggled(self, checked: bool) -> None:
        self.config.enable_audio_synth = checked
        if self.synth:
            if checked:
                self.synth.start()
            else:
                self.synth.stop()

    def _save_config(self) -> None:
        self.config.save("config.json")
        self._log_event("Configuration saved to config.json.")

    def hide_to_tray(self) -> None:
        if self.tray is not None or DaemonTrayIcon.isSystemTrayAvailable():
            if self.tray is None and self.orchestrator:
                self.tray = DaemonTrayIcon(orchestrator=self.orchestrator, parent=self)
                self.tray.show()
            self.hide()
            self._log_event("Dashboard minimized to system tray.")
        else:
            self.showMinimized()

    def _log_event(self, msg: str) -> None:
        t = time.strftime("%H:%M:%S")
        self.log_view.append(f"[{t}] {msg}")

    def closeEvent(self, event) -> None:
        self._stop_engine()
        event.accept()

