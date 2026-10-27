"""Unit tests for Daemon configuration."""

import json
from daemon.config import DaemonConfig


def test_default_config():
    config = DaemonConfig()
    assert config.model_name == "llama3.2:1b"
    assert config.anomaly_threshold == 0.75
    assert config.enable_audio_synth is True
    assert config.max_entities == 3


def test_load_save_config(tmp_path):
    config_file = tmp_path / "test_config.json"
    data = {
        "model_name": "qwen2.5:1.5b",
        "anomaly_threshold": 0.5,
        "enable_vision": False,
        "enable_audio_synth": False,
        "max_entities": 5,
        "check_interval_seconds": 1.0,
        "idle_threshold_seconds": 10.0,
        "anomaly_cooldown_seconds": 15.0,
        "sound_volume": 0.2,
        "debug_mode": True
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    loaded = DaemonConfig.load(config_file)
    assert loaded.model_name == "qwen2.5:1.5b"
    assert loaded.anomaly_threshold == 0.5
    assert loaded.enable_audio_synth is False
    assert loaded.debug_mode is True

