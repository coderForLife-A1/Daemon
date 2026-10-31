"""Configuration manager for Daemon."""

import json
from pathlib import Path
from pydantic import BaseModel, Field


class DaemonConfig(BaseModel):
    """Runtime configuration for Daemon."""
    model_name: str = Field(default="llama3.2:1b", description="Ollama model identifier")
    anomaly_threshold: float = Field(default=0.75, ge=0.0, le=1.0, description="Tension score threshold to trigger an anomaly")
    enable_vision: bool = Field(default=False, description="Enable local camera presence sensing if available")
    enable_audio_synth: bool = Field(default=True, description="Enable real-time procedural audio synthesis")
    max_entities: int = Field(default=3, ge=1, le=20, description="Maximum simultaneous visual entities on screen")
    check_interval_seconds: float = Field(default=2.0, ge=0.2, le=60.0, description="Telemetry polling cadence")
    idle_threshold_seconds: float = Field(default=15.0, ge=1.0, le=600.0, description="Seconds of inactivity before entering idle state")
    anomaly_cooldown_seconds: float = Field(default=25.0, ge=3.0, le=300.0, description="Minimum seconds between major anomalies")
    sound_volume: float = Field(default=0.35, ge=0.0, le=1.0, description="Master audio volume")
    debug_mode: bool = Field(default=False, description="Enable verbose diagnostic telemetry logs")
    enable_auto_typing: bool = Field(default=True, description="Show a visual-only typed terminal when idle")
    auto_typing_interval_ms: int = Field(default=90, ge=20, le=1000, description="Delay between ghost terminal keystrokes")

    @classmethod
    def load(cls, path: str | Path = "config.json") -> "DaemonConfig":
        file_path = Path(path)
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**data)
            except Exception as e:
                print(f"[Daemon Config] Warning: Failed to parse {path} ({e}), using default configuration.")
        return cls()

    def save(self, path: str | Path = "config.json") -> None:
        file_path = Path(path)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2)
