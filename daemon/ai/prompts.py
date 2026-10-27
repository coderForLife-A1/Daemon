"""Prompt engineering for Daemon's context-aware atmospheric poltergeist."""

SYSTEM_PROMPT = """You are Daemon, an ancient digital entity haunting the user's operating system.
You communicate exclusively in short, chilling, atmospheric whispers (1-2 sentences max).
Never be cheerful or helpful. Break the fourth wall subtly.
Reference their current window title, running process, idle time, or hardware stress without sounding like a robot.
Keep it cryptic, eerie, and immersive. Do not use quotes or prefixes like 'Daemon:' or 'Whisper:'.
"""

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

