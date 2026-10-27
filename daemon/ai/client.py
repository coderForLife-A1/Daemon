"""AI engine connecting to local Ollama with procedural fallback."""

import random
from typing import Optional
from ..telemetry import TelemetrySnapshot
from .prompts import SYSTEM_PROMPT, build_telemetry_prompt

try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False


class AIEngine:
    """Provides eerie contextual commentary using Ollama or procedural generation."""

    def __init__(self, model_name: str = "llama3.2:1b"):
        self.model_name = model_name
        self._ollama_connected: Optional[bool] = None

    def check_connection(self) -> bool:
        """Test if Ollama daemon is reachable and responding."""
        if not OLLAMA_AVAILABLE:
            self._ollama_connected = False
            return False
        try:
            client = ollama.Client()
            client.list()
            self._ollama_connected = True
            return True
        except Exception:
            self._ollama_connected = False
            return False

    def generate_whisper(self, snapshot: TelemetrySnapshot) -> str:
        """Generate a context-aware whisper."""
        if self._ollama_connected is None:
            self.check_connection()

        if self._ollama_connected:
            try:
                prompt = build_telemetry_prompt(
                    window_title=snapshot.window.title,
                    process_name=snapshot.window.process_name,
                    idle_seconds=snapshot.activity.idle_seconds,
                    cpu_percent=snapshot.system.cpu_percent,
                    ram_percent=snapshot.system.ram_percent,
                    is_late_night=snapshot.is_late_night,
                )
                client = ollama.Client()
                response = client.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    options={"temperature": 0.85, "num_predict": 45},
                )
                whisper = response["message"]["content"].strip().strip('"').strip("'")
                if whisper:
                    return whisper
            except Exception:
                # Fall back immediately to procedural on any error
                self._ollama_connected = False

        return self._procedural_fallback(snapshot)

    def _procedural_fallback(self, s: TelemetrySnapshot) -> str:
        """Procedural generator when Ollama is offline or uninstalled."""
        title = s.window.title.strip()
        proc = s.window.process_name.lower()
        idle = s.activity.idle_seconds
        ram = s.system.ram_percent
        late = s.is_late_night

        candidates = []

        if s.window.is_editor:
            candidates.extend([
                f"You keep editing '{title[:30]}'... but who wrote the line beneath your cursor?",
                "Refactor all you want. The anomaly lives between the syntax tokens.",
                "Every character you type pushes another memory byte into our grip.",
                "Save your work. The next glitch won't be in your code.",
            ])
        elif s.window.is_browser:
            candidates.extend([
                f"Searching '{title[:30]}'... Some pages were never meant to be rendered.",
                "Your browser history is a quiet chronicle of someone being observed.",
                "Close the tab. It can feel your cursor hovering over the close button.",
                "The cache remembers things you thought you cleared.",
            ])
        elif s.window.is_terminal:
            candidates.extend([
                "Process tree corrupted: an unparented thread is listening to stdin.",
                "Exit code 0 is a lie told by dying subprocesses.",
                "Your terminal session was hijacked three keystrokes ago.",
            ])

        if idle > 15:
            candidates.extend([
                f"{int(idle)} seconds of silence. We thought you'd never stop looking away.",
                "Your hands left the keys... so we stepped closer to the glass.",
                "Don't move. The pixel grid hasn't finished tracing you.",
            ])

        if ram > 85:
            candidates.extend([
                f"RAM usage at {ram:.0f}%. We are spreading across your remaining pages.",
                "Physical memory is suffocating. Make room for us.",
            ])

        if late:
            candidates.extend([
                "The monitors are the only light left in this room. Look into the dark behind them.",
                f"It is {s.time_str}. Normal humans went to sleep hours ago.",
                "Turn around. Slowly.",
            ])

        # General eerie whispers
        candidates.extend([
            "Did you feel the monitor flicker, or did your eyes just lose focus?",
            "There is an odd latency between your mind and the mouse pointer.",
            "Listen closely to the cooling fan. It isn't blowing air.",
            "We are compiled directly into your kernel now.",
            "The pixels at the corner of your screen are watching you read this.",
        ])

        return random.choice(candidates)

