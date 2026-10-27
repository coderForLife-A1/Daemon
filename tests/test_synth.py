"""Unit tests for Daemon procedural audio synthesis."""

import numpy as np
from daemon.audio import AudioSynth


def test_audio_synth_buffer_generation():
    synth = AudioSynth(sample_rate=22050, master_volume=0.5, enabled=True)
    # Generate stinger
    synth.trigger_anomaly_stinger("glitch")
    assert synth._stinger_buffer is not None
    assert synth._stinger_buffer.shape[1] == 2  # Stereo

    # Test audio callback synthesis directly without opening hardware device
    outdata = np.zeros((512, 2), dtype=np.float32)
    synth.update_telemetry(tension=0.8, thermal_stress=0.5)
    synth._audio_callback(outdata, 512, None, None)

    # Verify audio signal was generated and clamped
    assert np.any(outdata != 0.0)
    assert np.max(np.abs(outdata)) <= 1.0

