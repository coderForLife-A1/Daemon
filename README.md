# 👻 Daemon: An AI-Powered Desktop Poltergeist

> **A presence-aware, system-integrated haunted overlay driven entirely by local, open-weight AI models.**

Daemon turns your operating system into a reactive, atmospheric entity. Instead of relying on hardcoded timers or static jumpscares, Daemon continuously processes real-time system telemetry, active process states, and ambient presence to dynamically orchestrate contextual audio-visual anomalies across your desktop.

---

## 🏗 System Architecture

Daemon operates as a lightweight background architecture with zero cloud dependencies:
┌─────────────────────────┐     ┌──────────────────────────────┐
│  Telemetry & Sensors    │     │      Local AI Engine         │
│  - System Load / RAM    ├────►│  - Ollama / llama.cpp        │
│  - Active Window Title  │     │  - Vision / Presence Model   │
│  - Ambient Noise / Mic  │     │  - Open-Weight Audio Classifier│
└───────────┬─────────────┘     └──────────────┬───────────────┘
│                                  │
▼                                  ▼
┌──────────────────────────────────────────────────────────────┐
│                  Daemon Orchestrator                         │
│  - State Machine & Anomaly Trigger Engine                    │
└───────────┬──────────────────────────────────┬───────────────┘
│                                  │
▼                                  ▼
┌─────────────────────────┐     ┌──────────────────────────────┐
│  Transparent OS Canvas  │     │  Spatial Audio Generator     │
│  - Screen Crawlers      │     │  - Dynamic Thermal Hiss      │
│  - Terminal Injections  │     │  - Ambient Whispers          │
└─────────────────────────┘     └──────────────────────────────┘


---
## ✨ Features

* **👁 Presence-Aware Anomalies:** Monitors user activity and ambient inputs to trigger entities when attention shifts.
* **🧠 Context-Aware Whispers:** Leverages local open-weight LLMs (e.g., `Llama-3.2-1B` / `Qwen2.5`) to parse system logs or window titles and generate eerie, context-aware commentary.
* **🖥 Transparent Desktop Canvas:** Renders fluid, non-blocking visual entities across multi-monitor setups directly over active windows.
* **⚡ 100% Air-Gapped & Local:** Zero external API keys, zero network tracking, and complete privacy preservation—all inference happens locally on device hardware.

---

## 🛠 Tech Stack

* **Core Engine:** Python 3.11+ / Node.js
* **Local Inference:** `llama.cpp` / Ollama / TensorFlow.js / ONNX Runtime
* **OS Interfacing & Visual Overlay:** PySide6 (Qt) / Electron Transparent Window / `psutil`
* **Audio Processing:** PyAudio / Wave / Custom Audio Synth

---

## 🚀 Quickstart

### Prerequisites

1. Ensure Python 3.11+ is installed.
2. Install [Ollama](https://ollama.ai/) and pull a lightweight model:
   '''bash
   ollama pull llama3.2:1b
   '''

Installation
Clone the repository:

'''bash
git clone [https://github.com/your-username/daemon.git](https://github.com/your-username/daemon.git)
cd daemon
'''

Create and activate a virtual environment:
'''bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
'''
Install dependencies:

'''bash
pip install -r requirements.txt
Run the Daemon engine:
'''

'''bash
python main.py
'''

⚙️ Configuration
Control entity frequency, aggressive triggers, and model bindings via config.json:

JSON
{
  "model_name": "llama3.2:1b",
  "anomaly_threshold": 0.75,
  "enable_vision": false,
  "enable_audio_synth": true,
  "max_entities": 3
}

📜 License
Distributed under the MIT License. See LICENSE for details.