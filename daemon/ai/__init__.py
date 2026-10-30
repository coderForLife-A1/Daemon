"""AI and Whisper Generation Subsystem."""

from .client import AIEngine
from .prompts import (
    SYSTEM_PROMPT,
    CORRUPTED_KERNEL_SYSTEM_PROMPT,
    build_telemetry_prompt,
    build_corrupted_command_prompt,
)

__all__ = [
    "AIEngine",
    "SYSTEM_PROMPT",
    "CORRUPTED_KERNEL_SYSTEM_PROMPT",
    "build_telemetry_prompt",
    "build_corrupted_command_prompt",
]

