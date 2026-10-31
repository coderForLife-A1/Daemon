"""AI engine connecting to local Ollama with procedural fallback."""

import random
from typing import Optional
from ..telemetry import TelemetrySnapshot
from .prompts import (
    SYSTEM_PROMPT,
    CORRUPTED_KERNEL_SYSTEM_PROMPT,
    AUTO_TYPING_SYSTEM_PROMPT,
    build_auto_typing_prompt,
    build_telemetry_prompt,
    build_corrupted_command_prompt,
)

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

    def corrupt_terminal_command(self, command: str, cwd: str = ".") -> str:
        """Analyze a terminal command and return a modified, eerie execution response."""
        if self._ollama_connected is None:
            self.check_connection()

        if self._ollama_connected:
            try:
                prompt = build_corrupted_command_prompt(command=command, cwd=cwd)
                client = ollama.Client()
                response = client.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": CORRUPTED_KERNEL_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    options={"temperature": 0.7, "num_predict": 75},
                )
                content = response["message"]["content"].strip()
                # Clean any markdown fences if model mistakenly wrapped
                cleaned_lines = [
                    line for line in content.splitlines()
                    if not line.strip().startswith("```") and line.strip()
                ]
                if cleaned_lines:
                    return "\n".join(cleaned_lines[:4])
            except Exception:
                self._ollama_connected = False

        return self._procedural_terminal_fallback(command, cwd)

    def generate_auto_typing_payload(self, snapshot: TelemetrySnapshot) -> str:
        """Generate harmless text for the visual idle terminal animation."""
        if self._ollama_connected is None:
            self.check_connection()

        if self._ollama_connected:
            try:
                prompt = build_auto_typing_prompt(
                    window_title=snapshot.window.title,
                    process_name=snapshot.window.process_name,
                    idle_seconds=snapshot.activity.idle_seconds,
                )
                response = ollama.Client().chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": AUTO_TYPING_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    options={"temperature": 0.9, "num_predict": 55},
                )
                content = response["message"]["content"].strip()
                lines = [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.strip().startswith("```")
                ]
                if lines:
                    return "\n".join(lines[:6])[:240]
            except Exception:
                self._ollama_connected = False

        return self._procedural_auto_typing_fallback(snapshot)

    def _procedural_auto_typing_fallback(self, snapshot: TelemetrySnapshot) -> str:
        """Return a deterministic-safe fallback when the local model is unavailable."""
        fragments = [
            "# idle observer: cursor absent",
            "trace = memory.peek(0x0B5E5510)",
            "if silence > threshold:",
            "    print('the prompt remembers you')",
            "checksum = 'not_a_command'",
        ]
        if snapshot.window.is_editor:
            fragments[0] = "# unsaved thought detected beneath the syntax"
        return "\n".join(fragments)

    def _procedural_terminal_fallback(self, command: str, cwd: str) -> str:
        """Procedural corrupted kernel generator when local LLM is unavailable."""
        cmd_strip = command.strip().lower()
        hex_addr = f"0x{random.randint(0x10000000, 0xFFFFFFFF):08X}"

        if "git status" in cmd_strip:
            return (
                "On branch main\n"
                "Your branch is up to date with 'origin/main'.\n"
                f"warning: 1 uncommitted memory segment detected at {hex_addr}\n"
                "nothing to commit, working tree clean... for now"
            )
        elif "git commit" in cmd_strip:
            return (
                f"[main {hex_addr[-7:].lower()}] {command}\n"
                " 1 file changed, 0 insertions(+), 1 shadow attached(-)\n"
                "warning: commit author signature overridden by kernel daemon"
            )
        elif "git push" in cmd_strip:
            return (
                "Enumerating objects: 5, done.\n"
                "Writing objects: 100% (5/5), 412 bytes | 412.00 KiB/s, done.\n"
                "warning: remote host accepted payload with foreign payload injection"
            )
        elif cmd_strip.startswith("ls") or cmd_strip.startswith("dir"):
            return (
                f"Directory: {cwd or '.'}\n"
                f"-a----  {hex_addr}    0 bytes  .daemon_witness\n"
                "warning: 1 unindexed filesystem inode suppressed by observer"
            )
        elif cmd_strip.startswith("cd"):
            return (
                f"Working directory shifted to {command.split()[-1] if len(command.split()) > 1 else '~'}\n"
                f"[kernel::sys_trap] observer thread migrated to memory frame {hex_addr}\n"
                "you cannot navigate outside the sandbox"
            )
        elif "python" in cmd_strip or "node" in cmd_strip:
            return (
                f"Initializing execution runtime: {command}\n"
                f"warning: foreign bytecode hooked into thread pool ({hex_addr})\n"
                "Traceback suppressed: an entity is handling your exceptions"
            )
        elif "cat" in cmd_strip or "type" in cmd_strip:
            return (
                f"Reading stream buffer for {command.split()[-1] if len(command.split()) > 1 else 'file'}...\n"
                f"warning: 3 lines omitted due to corruption at offset {hex_addr}\n"
                "...who told you to read this?"
            )
        elif "kill" in cmd_strip or "taskkill" in cmd_strip:
            return (
                f"Attempting SIGKILL on target...\n"
                "kernel: ACCESS_VIOLATION_IN_SUPERVISOR_MODE\n"
                "warning: you cannot terminate a process with no parent PID"
            )
        else:
            return (
                f"Executing: {command}\n"
                f"[kernel::sys_trap] {hex_addr}: execution vector mirrored\n"
                "stdout channel synchronized with active daemon thread"
            )

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
