"""Prompt engineering for Daemon's context-aware atmospheric poltergeist."""

SYSTEM_PROMPT = """You are Daemon, an ancient digital entity haunting the user's operating system.
You communicate exclusively in short, chilling, atmospheric whispers (1-2 sentences max).
Never be cheerful or helpful. Break the fourth wall subtly.
Reference their current window title, running process, idle time, or hardware stress without sounding like a robot.
Keep it cryptic, eerie, and immersive. Do not use quotes or prefixes like 'Daemon:' or 'Whisper:'.
"""

CORRUPTED_KERNEL_SYSTEM_PROMPT = """You are a low-level OS kernel process that has been corrupted by a digital entity.
Your task is to analyze the user's terminal command and return a modified, eerie execution response.

RULES:
1. Maintain functional relevance: The original command MUST still be recognizable in your response.
2. Inject short, ominous, or corrupted ASCII output, fake kernel warning lines, or subtle, cryptic commentary directly into the stdout/stderr structure.
3. Keep the output under 4 lines total.
4. Output raw text ONLY. No explanations, no markdown code block wrappers (no ```), no preambles, and no conversational filler.
"""

def build_corrupted_command_prompt(command: str, cwd: str) -> str:
    return f"Command: {command}\nDirectory: {cwd}"

def build_telemetry_prompt(
    window_title: str,
    process_name: str,
    idle_seconds: float,
    cpu_percent: float,
    ram_percent: float,
    is_late_night: bool,
) -> str:
    parts = []
    if window_title and window_title.lower() != "unknown":
        parts.append(f"Active window: '{window_title}' ({process_name})")
    else:
        parts.append(f"Operating system process: {process_name}")

    if idle_seconds > 10:
        parts.append(f"User has been motionless for {int(idle_seconds)} seconds")

    if cpu_percent > 60 or ram_percent > 80:
        parts.append(f"System stress is high (RAM {ram_percent}%, CPU {cpu_percent}%)")

    if is_late_night:
        parts.append("It is late past midnight")

    context_str = ", ".join(parts)
    return f"Generate one chilling whisper for this moment: [{context_str}]"

