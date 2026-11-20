# 👻 Daemon

> **A local, AI-assisted desktop poltergeist for Windows.**

Daemon watches the rhythm of your desktop and turns quiet moments into
atmospheric anomalies: whispers, glitches, crawlers, watchers, procedural
audio, and a harmless ghost terminal. Everything runs locally, with optional
Ollama-powered text generation and procedural fallbacks when no model is
available.

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square&logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/AI-local%20Ollama-111827?style=flat-square" alt="Local Ollama">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-22C55E?style=flat-square" alt="MIT License"></a>
</p>

## What it does

- **Reads presence signals** such as activity, active window, system load, and
  optional ambient audio.
- **Dispatches anomalies** through a transparent, click-through,
  multi-monitor overlay.
- **Creates atmosphere** with procedural sound synthesis and context-aware
  whispers.
- **Stays local** with optional [Ollama](https://ollama.com/) integration and
  built-in procedural fallbacks.
- **Provides control** through a system-tray icon and a dark desktop control
  center.
- **Includes a visual-only ghost terminal** that displays harmless generated
  fragments without focusing, executing, or modifying a real shell.

## How it works

```text
┌────────────────────┐
│ Desktop telemetry  │──┐
│ Activity + system  │  │
│ Window + audio     │  ▼
└────────────────────┘  Orchestrator ──┬── Overlay effects
┌────────────────────┐                 ├── Procedural audio
│ Local AI (optional)│─────────────────┤
└────────────────────┘                 ├── System tray
                                       └── Ghost terminal
```

The orchestrator combines telemetry into a tension score, respects cooldowns
and entity limits, and decides when an anomaly should appear.

## Quick start

### 1. Install

```powershell
git clone https://github.com/coderForLife-A1/Daemon.git
cd Daemon
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell activation is unavailable, use the virtual environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Launch

Open the desktop control center:

```powershell
python app.py
```

Or launch the background daemon directly:

```powershell
python main.py
```

On Windows, [`run.bat`](run.bat) is also available as a double-click launcher.

### 3. Optional: enable local AI

Install Ollama, start its local service, and pull the model selected in
[`config.json`](config.json):

```powershell
ollama pull phi3:mini
```

Daemon continues to work without a running Ollama service by using procedural
text generation.

## Command-line usage

```text
python main.py [options]
```

| Option | Description |
| --- | --- |
| `--config PATH` | Load a different JSON configuration file. |
| `--threshold VALUE` | Override the anomaly threshold (`0.0`–`1.0`). |
| `--no-audio` | Disable audio synthesis for this run. |
| `--no-overlay` | Run telemetry and orchestration without the visual overlay. |
| `--gui` | Open the desktop control center instead of the background daemon. |
| `--test-anomaly TYPE` | Trigger `whisper`, `crawler`, `glitch`, `watcher`, `terminal`, or `auto_typing` on startup. |
| `--terminal-inject COMMAND` | Generate a simulated eerie response for a command; does not execute it. |
| `--powershell-hook` | Print an optional PowerShell profile integration snippet. |
| `--debug` | Enable verbose telemetry output. |

Try a visual effect without sound:

```powershell
python main.py --no-audio --test-anomaly glitch
```

Stop the daemon with `Ctrl+C`, or use the system-tray menu.

> **Terminal note:** The `--terminal-inject` mode is designed for generated
> commentary and does not run the supplied command. Treat the optional
> PowerShell hook as an opt-in developer convenience and review generated
> snippets before adding them to a profile.

## Configuration

Runtime settings live in [`config.json`](config.json). The checked-in
configuration uses these defaults:

| Setting | Default | Description |
| --- | ---: | --- |
| `model_name` | `phi3:mini` | Ollama model used for generated text. |
| `anomaly_threshold` | `0.1` | Tension score required to trigger an anomaly. |
| `enable_vision` | `false` | Enable local camera presence sensing when supported. |
| `enable_audio_synth` | `true` | Enable procedural sound effects. |
| `max_entities` | `3` | Maximum simultaneous overlay entities. |
| `check_interval_seconds` | `2.0` | Telemetry polling interval. |
| `idle_threshold_seconds` | `15.0` | Seconds of inactivity before the idle state begins. |
| `anomaly_cooldown_seconds` | `25.0` | Minimum delay between major anomalies. |
| `sound_volume` | `0.35` | Master volume from `0.0` to `1.0`. |
| `debug_mode` | `false` | Enable diagnostic telemetry logging. |
| `enable_auto_typing` | `true` | Enable the visual-only ghost terminal. |
| `auto_typing_interval_ms` | `90` | Delay between ghost terminal keystrokes. |

Configuration is validated with Pydantic. If the file is missing or cannot be
parsed, Daemon reports a warning and uses built-in defaults.

## Project layout

```text
Daemon/
├── app.py                 # Desktop control center launcher
├── main.py                # Background daemon and CLI entry point
├── config.json            # Runtime configuration
├── daemon/
│   ├── ai/                # Ollama client and procedural fallbacks
│   ├── audio/             # Procedural audio synthesis
│   ├── orchestrator/      # Tension scoring and anomaly dispatch
│   ├── overlay/           # Transparent overlay and visual effects
│   ├── telemetry/         # Activity, audio, system, and window sensors
│   ├── terminal/          # Ghost terminal and optional integration
│   └── ui/                # Dashboard and system-tray controls
└── tests/                 # Automated test suite
```

## Development

Run the test suite from the repository root:

```powershell
python -m pytest
```

The tests cover configuration, orchestration, overlay effects, audio
synthesis, AI behavior, telemetry, the dashboard, and terminal components.

## Privacy

Daemon is intended to run locally. It reads desktop telemetry and may take
short ambient-audio samples when the audio sensor is enabled. Audio samples
are analyzed in memory and are not intentionally uploaded or persisted.
Review the telemetry and audio settings before running Daemon in a shared or
sensitive environment.

## License

Daemon is distributed under the [MIT License](LICENSE).
