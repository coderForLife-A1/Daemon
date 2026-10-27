"""Ambient audio / noise sensor."""

import numpy as np
from pydantic import BaseModel

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except Exception:
    SOUNDDEVICE_AVAILABLE = False


class AudioSensorMetrics(BaseModel):
    ambient_noise_level: float = 0.0  # RMS normalized between 0.0 and 1.0
    mic_active: bool = False


class AudioSensor:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and SOUNDDEVICE_AVAILABLE
        self._last_level = 0.0
        self._mic_available = False
        if self.enabled:
            self._probe_device()

    def _probe_device(self) -> None:
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d.get('max_input_channels', 0) > 0]
            self._mic_available = len(input_devices) > 0
        except Exception:
            self._mic_available = False

    def read(self) -> AudioSensorMetrics:
        if not self.enabled or not self._mic_available:
            return AudioSensorMetrics(ambient_noise_level=0.0, mic_active=False)

        try:
            # Quick 50ms passive recording sample (800 samples at 16kHz)
            sample_rate = 16000
            duration = 0.05
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32",
                blocking=True
            )
            rms = float(np.sqrt(np.mean(np.square(recording))))
            # Normalize and clamp to 0.0 - 1.0
            normalized = min(1.0, max(0.0, rms * 5.0))
            self._last_level = round(normalized, 3)
            return AudioSensorMetrics(ambient_noise_level=self._last_level, mic_active=True)
        except Exception:
            return AudioSensorMetrics(ambient_noise_level=0.0, mic_active=False)

