# Daemon

> An AI-powered desktop poltergeist that reacts to your activity.

Daemon is a local Python application that turns desktop telemetry into
atmospheric audio and visual anomalies. It monitors signals such as system
load, the active window, keyboard/mouse inactivity, and ambient audio, then
uses an orchestrator to decide when to display an effect or play a sound.

The optional Ollama integration generates context-aware whispers. If Ollama is
unavailable, Daemon uses a built-in procedural fallback, so the core experience
does not require a cloud service or API key.

## Features

- Presence-aware anomaly triggers based on activity and system telemetry.
- Transparent, multi-monitor overlay effects:
  whispers, crawlers, glitches, and watchers.
- Procedural audio synthesis with configurable volume.
- Optional local LLM support through [Ollama](https://ollama.com/).
- System-tray controls and a headless fallback when no tray is available.
- A visual-only, semi-transparent ghost terminal that types harmless generated fragments while idle.
- Command-line options for testing effects and overriding configuration.

## How it works

```text
Telemetry sensors ──┐
                    ├──> Orchestrator ──> Overlay effects
Local AI (optional) ┘             └──────> Audio synthesis
                                      └──> System tray
```

## Requirements

- Python 3.11 or newer.
- A desktop environment supported by Qt/PySide6.
- An audio output device for sound effects.
- [Ollama](https://ollama.com/) is optional. Install it only if you want
  locally generated, context-aware whispers.

The project currently targets desktop use on Windows. Some telemetry and audio
features may require additional permissions or platform-specific audio
drivers.

## Installation

Clone the repository and create a virtual environment:

```powershell
git clone https://github.com/coderForLife-A1/Daemon.git
cd Daemon
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, you can run the environment's interpreter
directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Optional Ollama setup

Install Ollama, start its local service, and pull the model configured in
[`config.json`](config.json):

```powershell
ollama pull llama3.2:1b
```

Daemon still starts without Ollama and falls back to procedural whispers.

## Usage

Start Daemon with the default configuration:

```powershell
python main.py
```

Useful command-line options:

| Option | Description |
| --- | --- |
| `--config PATH` | Load a different JSON configuration file. |
| `--threshold VALUE` | Override the anomaly threshold (`0.0`–`1.0`). |
| `--no-audio` | Disable audio synthesis for the current run. |
| `--no-overlay` | Run telemetry and orchestration without the visual overlay. |
| `--test-anomaly TYPE` | Trigger `whisper`, `crawler`, `glitch`, `watcher`, `terminal`, or `auto_typing` on startup. |
| `--debug` | Enable verbose diagnostic telemetry output. |

For example, to test an effect without audio:

```powershell
python main.py --no-audio --test-anomaly glitch
```

Stop the application with `Ctrl+C` or use the system-tray menu.

## Configuration

Runtime defaults are stored in [`config.json`](config.json). The main settings
are:

| Setting | Purpose |
| --- | --- |
| `model_name` | Ollama model used for whispers. |
| `anomaly_threshold` | Tension score required to trigger an anomaly. |
| `enable_vision` | Enable local camera presence sensing when supported. |
| `enable_audio_synth` | Enable procedural sound effects. |
| `max_entities` | Maximum simultaneous overlay entities. |
| `check_interval_seconds` | Telemetry polling interval. |
| `idle_threshold_seconds` | Inactivity period before the idle state begins. |
| `anomaly_cooldown_seconds` | Minimum delay between major anomalies. |
| `sound_volume` | Master volume from `0.0` to `1.0`. |
| `debug_mode` | Enable diagnostic telemetry logging. |
| `enable_auto_typing` | Show the visual-only ghost terminal during an idle anomaly. |
| `auto_typing_interval_ms` | Milliseconds between simulated ghost keystrokes. |

The auto-typing terminal is intentionally isolated from the real shell: it is
read-only, never focuses or executes commands, and can be closed like any
other window.

The configuration is validated with Pydantic. Invalid or missing configuration
files fall back to the built-in defaults.

## Development

Run the test suite from the repository root:

```powershell
python -m pytest
```

The tests cover configuration, orchestration, overlay effects, audio
synthesis, AI behavior, and telemetry components.

## Privacy

Daemon is designed to run locally. It reads desktop telemetry and may take
short ambient-audio samples when the audio sensor is enabled. Audio samples
are analyzed in memory and are not intentionally uploaded or persisted.
Review and adjust the telemetry and audio settings before running Daemon in a
shared or sensitive environment.

## License

Distributed under the [MIT License](LICENSE).
