"""Unit tests for Daemon telemetry sensors."""

from daemon.telemetry import TelemetryHub, TelemetrySnapshot, AttentionState


def test_telemetry_capture():
    hub = TelemetryHub(idle_threshold=10.0, enable_mic=False)
    snapshot = hub.capture()

    assert isinstance(snapshot, TelemetrySnapshot)
    assert snapshot.system.ram_percent >= 0.0
    assert snapshot.system.ram_total_gb > 0.0
    assert snapshot.activity.attention_state in [
        AttentionState.ACTIVE,
        AttentionState.DRIFTING,
        AttentionState.IDLE,
        AttentionState.ABSENT,
    ]
    assert isinstance(snapshot.activity.cursor_position, tuple)
    assert len(snapshot.activity.cursor_position) == 2
    assert snapshot.window.title is not None

