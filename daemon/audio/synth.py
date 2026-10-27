"""Real-time procedural audio synthesizer for Daemon.

Generates dynamic thermal hiss, low-frequency binaural drones,
and procedural anomaly stingers using numpy and sounddevice.
"""

import threading
import time
import numpy as np
from typing import Optional

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except Exception:
    SOUNDDEVICE_AVAILABLE = False


class AudioSynth:
    """Procedural spatial and atmospheric sound generator."""

    def __init__(self, sample_rate: int = 44100, master_volume: float = 0.35, enabled: bool = True):
        self.sample_rate = sample_rate
        self.master_volume = max(0.0, min(1.0, master_volume))
        self.enabled = enabled and SOUNDDEVICE_AVAILABLE

        # Synthesis state
        self._is_running = False
        self._tension = 0.0          # 0.0 - 1.0
        self._thermal_stress = 0.0   # 0.0 - 1.0
        self._phase_drone_l = 0.0
        self._phase_drone_r = 0.0
        self._stinger_buffer: Optional[np.ndarray] = None
        self._stinger_idx = 0
        self._lock = threading.Lock()
        self._stream: Optional[sd.OutputStream] = None

    def start(self) -> bool:
        """Start the real-time audio output stream."""
        if not self.enabled or self._is_running:
            return False

        try:
            self._is_running = True
            self._stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=2,
                dtype="float32",
                callback=self._audio_callback,
                blocksize=1024,
            )
            self._stream.start()
            return True
        except Exception as e:
            self._is_running = False
            self.enabled = False
            return False

    def stop(self) -> None:
        """Stop audio output stream."""
        self._is_running = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    def update_telemetry(self, tension: float, thermal_stress: float) -> None:
        """Update live telemetry parameters driving the synthesis."""
        with self._lock:
            self._tension = max(0.0, min(1.0, tension))
            self._thermal_stress = max(0.0, min(1.0, thermal_stress))

    def trigger_anomaly_stinger(self, kind: str = "glitch") -> None:
        """Generate and queue a sudden procedural horror stinger."""
        if not self.enabled:
            return

        duration = 0.6 if kind == "glitch" else 1.2
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)

        if kind == "glitch":
            # Rapid frequency modulated down-chirp + crackle
            freq = 600 * np.exp(-t * 6.0) + 120
            tone = 0.4 * np.sin(2 * np.pi * freq * t)
            noise = (np.random.rand(len(t)) - 0.5) * 0.3 * np.exp(-t * 4.0)
            # Granular pops
            pops = (np.random.rand(len(t)) > 0.98).astype(np.float32) * (np.random.rand(len(t)) - 0.5) * 0.8
            stinger = (tone + noise + pops) * np.exp(-t * 3.5)
        elif kind == "whisper":
            # Spectral breath / resonant whisper murmur
            noise = (np.random.rand(len(t)) - 0.5)
            # Simple resonant bandpass modulation
            envelope = np.sin(np.pi * t / duration) ** 2
            f1 = 440 + 80 * np.sin(2 * np.pi * 3.0 * t)
            stinger = noise * np.sin(2 * np.pi * f1 * t) * envelope * 0.4
        else:
            # Sub bass drop
            freq = 90 * np.exp(-t * 2.0) + 35
            stinger = 0.6 * np.sin(2 * np.pi * freq * t) * np.exp(-t * 1.5)

        # Stereo pan with slight delay
        stinger_stereo = np.column_stack([stinger, np.roll(stinger, 24)])

        with self._lock:
            self._stinger_buffer = stinger_stereo.astype(np.float32)
            self._stinger_idx = 0

    def _audio_callback(self, outdata: np.ndarray, frames: int, time_info, status) -> None:
        """Real-time sounddevice audio callback."""
        with self._lock:
            tension = self._tension
            thermal = self._thermal_stress
            vol = self.master_volume

        # 1. Low frequency binaural drone (swells with tension)
        # Left: 52 Hz, Right: 55 Hz (3 Hz delta creates creeping psychoacoustic beat)
        freq_l = 52.0
        freq_r = 55.0
        t_block = np.arange(frames) / self.sample_rate

        drone_l = np.sin(2 * np.pi * freq_l * t_block + self._phase_drone_l)
        drone_r = np.sin(2 * np.pi * freq_r * t_block + self._phase_drone_r)
        self._phase_drone_l = (self._phase_drone_l + 2 * np.pi * freq_l * frames / self.sample_rate) % (2 * np.pi)
        self._phase_drone_r = (self._phase_drone_r + 2 * np.pi * freq_r * frames / self.sample_rate) % (2 * np.pi)

        # Scale drone by tension (whisper-quiet at 0, subtle throbbing at 1.0)
        drone_gain = (tension ** 2) * 0.18
        drone_out = np.column_stack([drone_l, drone_r]) * drone_gain

        # 2. Dynamic Thermal Hiss (scales with CPU/RAM stress)
        hiss_raw = (np.random.rand(frames, 2) - 0.5) * 2.0
        hiss_gain = (thermal ** 1.5) * 0.08
        hiss_out = hiss_raw * hiss_gain

        out = drone_out + hiss_out

        # 3. Layer queued stinger if active
        with self._lock:
            if self._stinger_buffer is not None:
                rem = len(self._stinger_buffer) - self._stinger_idx
                take = min(frames, rem)
                out[:take] += self._stinger_buffer[self._stinger_idx : self._stinger_idx + take] * 0.7
                self._stinger_idx += take
                if self._stinger_idx >= len(self._stinger_buffer):
                    self._stinger_buffer = None

        # Master gain & safety limiter
        out = np.clip(out * vol, -1.0, 1.0)
        outdata[:] = out.astype(np.float32)
