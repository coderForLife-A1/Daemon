"""Unit tests for Daemon AI whisper engine."""

from daemon.telemetry import TelemetryHub
from daemon.ai import AIEngine, build_telemetry_prompt, SYSTEM_PROMPT


def test_build_telemetry_prompt():
    prompt = build_telemetry_prompt(
        window_title="main.py - Daemon",
        process_name="code.exe",
        idle_seconds=22.0,
        cpu_percent=45.0,
        ram_percent=88.0,
        is_late_night=True,
    )
    assert "Active window: 'main.py - Daemon'" in prompt
    assert "motionless for 22 seconds" in prompt
    assert "System stress is high" in prompt
    assert "late past midnight" in prompt


def test_ai_whisper_generation():
    hub = TelemetryHub(enable_mic=False)
    snapshot = hub.capture()

    engine = AIEngine()
    whisper = engine.generate_whisper(snapshot)
    assert isinstance(whisper, str)
    assert len(whisper) > 5

