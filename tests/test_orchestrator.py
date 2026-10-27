"""Unit tests for the Daemon state machine and orchestrator."""

from daemon.telemetry import (
    TelemetrySnapshot,
    SystemMetrics,
    WindowMetrics,
    ActivityMetrics,
    AttentionState,
    AudioSensorMetrics,
)
from daemon.orchestrator import OrchestratorStateMachine, HauntState


def make_snapshot(idle: float = 0.0, stress: float = 0.1, late: bool = False):
    return TelemetrySnapshot(
        system=SystemMetrics(cpu_percent=10, ram_percent=30, thermal_stress_index=stress),
        window=WindowMetrics(title="Code", process_name="code.exe", is_editor=True),
        activity=ActivityMetrics(idle_seconds=idle, attention_state=AttentionState.ACTIVE),
        audio=AudioSensorMetrics(),
    )


def test_state_machine_transitions():
    sm = OrchestratorStateMachine(anomaly_threshold=0.6, cooldown_seconds=5.0)

    # Active user: low tension -> DORMANT or OBSERVING
    snap_active = make_snapshot(idle=0.5, stress=0.1)
    state, should_trigger = sm.evaluate(snap_active)
    assert should_trigger is False
    assert sm.tension < 0.5

    # Idle user with high stress: tension rises -> HAUNTING
    snap_idle = make_snapshot(idle=35.0, stress=0.9, late=True)
    triggered_any = False
    for _ in range(5):
        state, should_trigger = sm.evaluate(snap_idle)
        if should_trigger:
            triggered_any = True
            break

    assert triggered_any is True
    assert state == HauntState.HAUNTING

    # Immediate next cycle must enter COOLDOWN
    state_after, trigger_after = sm.evaluate(snap_idle)
    assert state_after == HauntState.COOLDOWN
    assert trigger_after is False
