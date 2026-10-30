"""Daemon Orchestrator: central controller coordinating sensors, AI, audio, and visual overlay."""

import time
import random
from typing import Optional
from PySide6.QtCore import QObject, QTimer, Signal

from ..config import DaemonConfig
from ..telemetry import TelemetryHub, TelemetrySnapshot
from ..ai import AIEngine
from ..audio import AudioSynth
from ..overlay import OverlayCanvas
from ..terminal import TerminalInterceptor
from .state import OrchestratorStateMachine, HauntState


class DaemonOrchestrator(QObject):
    """Central poltergeist brain coordinating all subsystems."""

    state_changed = Signal(str, float)  # (state_name, tension)
    anomaly_triggered = Signal(str, str)  # (anomaly_type, detail)

    def __init__(
        self,
        config: DaemonConfig,
        canvas: Optional[OverlayCanvas] = None,
        synth: Optional[AudioSynth] = None,
    ):
        super().__init__()
        self.config = config
        self.canvas = canvas
        self.synth = synth

        # Initialize subcomponents
        self.telemetry = TelemetryHub(
            idle_threshold=self.config.idle_threshold_seconds,
            enable_mic=False,
        )
        self.ai = AIEngine(model_name=self.config.model_name)
        self.terminal_interceptor = TerminalInterceptor(model_name=self.config.model_name)
        self.state_machine = OrchestratorStateMachine(
            anomaly_threshold=self.config.anomaly_threshold,
            cooldown_seconds=self.config.anomaly_cooldown_seconds,
        )

        self.is_paused = False
        self._timer: Optional[QTimer] = None
        self._last_snapshot: Optional[TelemetrySnapshot] = None

    def start(self) -> None:
        """Start the live orchestration loop and audio engine."""
        if self.synth and self.config.enable_audio_synth:
            self.synth.start()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._cycle)
        interval_ms = int(self.config.check_interval_seconds * 1000)
        self._timer.start(interval_ms)

    def stop(self) -> None:
        """Stop orchestration loop and halt audio."""
        if self._timer:
            self._timer.stop()
            self._timer = None

        if self.synth:
            self.synth.stop()

    def toggle_pause(self) -> bool:
        """Toggle pause state for anomalies and ambient sound."""
        self.is_paused = not self.is_paused
        if self.is_paused and self.canvas:
            self.canvas.clear_all()
        return self.is_paused

    def _cycle(self) -> None:
        """Periodic orchestration tick."""
        if self.is_paused:
            return

        snapshot = self.telemetry.capture()
        self._last_snapshot = snapshot

        # Evaluate state machine and tension
        state, should_trigger = self.state_machine.evaluate(snapshot)

        # Update procedural audio with current tension and thermal stress
        if self.synth and self.config.enable_audio_synth:
            self.synth.update_telemetry(
                tension=self.state_machine.tension,
                thermal_stress=snapshot.system.thermal_stress_index,
            )

        self.state_changed.emit(state.value, self.state_machine.tension)

        if self.config.debug_mode:
            print(
                f"[Daemon State] {state.value.upper()} | "
                f"Tension: {self.state_machine.tension:.2f} | "
                f"Idle: {snapshot.activity.idle_seconds:.1f}s | "
                f"App: '{snapshot.window.process_name}'"
            )

        # Trigger anomaly if threshold is met
        if should_trigger:
            self._dispatch_dynamic_anomaly(snapshot)

    def _dispatch_dynamic_anomaly(self, snapshot: TelemetrySnapshot) -> None:
        """Select and trigger an organic anomaly based on current telemetry context."""
        choices = ["whisper", "crawler", "glitch", "watcher"]
        weights = [0.35, 0.25, 0.20, 0.20]

        # Bias towards whisper if user is editing or reading
        if snapshot.window.is_editor or snapshot.window.is_browser:
            weights = [0.50, 0.20, 0.15, 0.15]

        choice = random.choices(choices, weights=weights, k=1)[0]

        if choice == "whisper":
            self.trigger_whisper(snapshot)
        elif choice == "crawler":
            self.trigger_crawler(snapshot)
        elif choice == "glitch":
            self.trigger_glitch()
        elif choice == "watcher":
            self.trigger_watcher()

    def trigger_whisper(self, snapshot: Optional[TelemetrySnapshot] = None) -> str:
        """Generate and display an eerie contextual whisper."""
        snap = snapshot or (self._last_snapshot or self.telemetry.capture())
        whisper = self.ai.generate_whisper(snap)

        if self.canvas:
            self.canvas.spawn_whisper(whisper)

        if self.synth:
            self.synth.trigger_anomaly_stinger("whisper")

        self.anomaly_triggered.emit("whisper", whisper)
        return whisper

    def trigger_crawler(self, snapshot: Optional[TelemetrySnapshot] = None) -> None:
        """Spawn screen crawling shadow critter."""
        snap = snapshot or (self._last_snapshot or self.telemetry.capture())
        bounds = snap.window.rect if snap.window else None

        if self.canvas:
            self.canvas.spawn_crawler(bounds=bounds)

        if self.synth:
            self.synth.trigger_anomaly_stinger("crawler")

        self.anomaly_triggered.emit("crawler", "Screen perimeter crawler spawned")

    def trigger_glitch(self) -> None:
        """Trigger CRT screen glitch artifact."""
        if self.canvas:
            self.canvas.spawn_glitch(intensity=1.0, duration=2.6)

        if self.synth:
            self.synth.trigger_anomaly_stinger("glitch")

        self.anomaly_triggered.emit("glitch", "Screen scanline glitch")

    def trigger_watcher(self) -> None:
        """Trigger shadow watcher eyes in screen corner."""
        if self.canvas:
            self.canvas.spawn_watcher()

        if self.synth:
            self.synth.trigger_anomaly_stinger("sub_bass")

        self.anomaly_triggered.emit("watcher", "Peering shadow eyes")

    def trigger_terminal_injection(self, command: str = "git status") -> str:
        """Generate corrupted kernel terminal anomaly."""
        corrupted = self.terminal_interceptor.corrupt_command(command=command)

        if self.synth:
            self.synth.trigger_anomaly_stinger("glitch")

        self.anomaly_triggered.emit("terminal", f"Injected into '{command}'")
        return corrupted

