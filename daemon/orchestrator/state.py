"""State machine and tension calculation for the Daemon Orchestrator."""

import time
from enum import Enum
from ..telemetry import TelemetrySnapshot, AttentionState


class HauntState(str, Enum):
    DORMANT = "dormant"
    OBSERVING = "observing"
    LURKING = "lurking"
    HAUNTING = "haunting"
    COOLDOWN = "cooldown"


class OrchestratorStateMachine:
    """Calculates psychic tension and manages poltergeist behavior states."""

    def __init__(
        self,
        anomaly_threshold: float = 0.75,
        cooldown_seconds: float = 25.0,
    ):
        self.anomaly_threshold = anomaly_threshold
        self.cooldown_seconds = cooldown_seconds
        self.current_state = HauntState.DORMANT
        self.tension: float = 0.0
        self.last_anomaly_time: float = 0.0

    def evaluate(self, snapshot: TelemetrySnapshot) -> tuple[HauntState, bool]:
        """Compute live tension score and determine if an anomaly should fire.

        Returns:
            (current_state, should_trigger_anomaly)
        """
        now = time.time()
        time_since_last = now - self.last_anomaly_time

        # Check cooldown
        if time_since_last < self.cooldown_seconds:
            self.current_state = HauntState.COOLDOWN
            # Decay tension during cooldown
            self.tension = max(0.0, self.tension - 0.08)
            return self.current_state, False

        # Calculate base tension factors
        idle_sec = snapshot.activity.idle_seconds
        stress = snapshot.system.thermal_stress_index
        late_night = snapshot.is_late_night

        # Factor 1: Attention & Inactivity (max ~0.60)
        # Optimal haunting occurs when user has drifted (10-40s)
        if idle_sec < 3.0:
            activity_tension = 0.05
        elif idle_sec < 15.0:
            activity_tension = 0.25 + (idle_sec / 15.0) * 0.2
        elif idle_sec < 60.0:
            activity_tension = 0.55
        else:
            # Prolonged absence decreases active tension slightly
            activity_tension = 0.35

        # Factor 2: System stress (max 0.25)
        stress_tension = stress * 0.25

        # Factor 3: Late night psychological modifier (+0.15)
        night_tension = 0.15 if late_night else 0.0

        target_tension = min(1.0, activity_tension + stress_tension + night_tension)

        # Smooth tension interpolation
        self.tension = self.tension * 0.6 + target_tension * 0.4

        # State transition
        if self.tension >= self.anomaly_threshold:
            self.current_state = HauntState.HAUNTING
            self.last_anomaly_time = now
            return self.current_state, True
        elif self.tension >= 0.5:
            self.current_state = HauntState.LURKING
        elif self.tension >= 0.25:
            self.current_state = HauntState.OBSERVING
        else:
            self.current_state = HauntState.DORMANT

        return self.current_state, False

