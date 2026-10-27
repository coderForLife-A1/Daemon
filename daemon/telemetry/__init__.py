"""Telemetry subsystem aggregating system, window, user activity, and ambient sensors."""

import time
from datetime import datetime
from pydantic import BaseModel, Field

from .system import SystemSensor, SystemMetrics
from .window import WindowSensor, WindowMetrics
from .activity import ActivitySensor, ActivityMetrics, AttentionState
from .audio_sensor import AudioSensor, AudioSensorMetrics


class TelemetrySnapshot(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    time_str: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    system: SystemMetrics
    window: WindowMetrics
    activity: ActivityMetrics
    audio: AudioSensorMetrics

    @property
    def is_late_night(self) -> bool:
        """True if current hour is between 11 PM and 5 AM."""
        hour = datetime.now().hour
        return hour >= 23 or hour < 5


class TelemetryHub:
    """Central collector for all live sensors."""

    def __init__(self, idle_threshold: float = 15.0, enable_mic: bool = False):
        self.system_sensor = SystemSensor()
        self.window_sensor = WindowSensor()
        self.activity_sensor = ActivitySensor(idle_threshold=idle_threshold)
        self.audio_sensor = AudioSensor(enabled=enable_mic)

    def capture(self) -> TelemetrySnapshot:
        sys_metrics = self.system_sensor.read()
        win_metrics = self.window_sensor.read()
        act_metrics = self.activity_sensor.read()
        aud_metrics = self.audio_sensor.read()

        return TelemetrySnapshot(
            system=sys_metrics,
            window=win_metrics,
            activity=act_metrics,
            audio=aud_metrics,
        )


__all__ = [
    "TelemetryHub",
    "TelemetrySnapshot",
    "SystemMetrics",
    "WindowMetrics",
    "ActivityMetrics",
    "AttentionState",
    "AudioSensorMetrics",
]

