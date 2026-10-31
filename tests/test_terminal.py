"""Unit tests for the Terminal Injection subsystem."""

from PySide6.QtWidgets import QApplication
from daemon.ai.prompts import (
    AUTO_TYPING_SYSTEM_PROMPT,
    CORRUPTED_KERNEL_SYSTEM_PROMPT,
    build_auto_typing_prompt,
    build_corrupted_command_prompt,
)
from daemon.terminal import GhostTerminalWindow, TerminalInterceptor
from daemon.config import DaemonConfig
from daemon.orchestrator import DaemonOrchestrator
from daemon.ui import DaemonDashboard


def test_corrupted_command_prompt_builder():
    prompt = build_corrupted_command_prompt(command="git status", cwd="/projects/daemon")
    assert "Command: git status" in prompt
    assert "Directory: /projects/daemon" in prompt
    assert "You are a low-level OS kernel process" in CORRUPTED_KERNEL_SYSTEM_PROMPT


def test_terminal_interceptor_git_status():
    interceptor = TerminalInterceptor()
    output = interceptor.corrupt_command("git status", cwd="/projects/daemon")

    # Rule checks
    lines = [line for line in output.splitlines() if line.strip()]
    assert len(lines) <= 4
    assert any("branch" in l.lower() or "git" in l.lower() for l in lines)
    assert any("warning" in l.lower() or "memory" in l.lower() for l in lines)
    assert not output.strip().startswith("```")


def test_terminal_interceptor_various_commands():
    interceptor = TerminalInterceptor()

    # ls / dir
    ls_out = interceptor.corrupt_command("ls -la", cwd="C:/Users/test")
    assert len(ls_out.splitlines()) <= 4
    assert "daemon_witness" in ls_out or "inode" in ls_out or "Directory:" in ls_out

    # python
    py_out = interceptor.corrupt_command("python main.py")
    assert len(py_out.splitlines()) <= 4
    assert "python" in py_out.lower() or "runtime" in py_out.lower() or "entity" in py_out.lower()

    # kill
    kill_out = interceptor.corrupt_command("kill -9 1234")
    assert len(kill_out.splitlines()) <= 4
    assert "kill" in kill_out.lower() or "violation" in kill_out.lower() or "process" in kill_out.lower()


def test_powershell_hook_generation():
    hook = TerminalInterceptor.get_powershell_hook_script()
    assert "Invoke-Daemon" in hook
    assert "python -m daemon.terminal" in hook


def test_orchestrator_terminal_injection():
    config = DaemonConfig()
    orchestrator = DaemonOrchestrator(config=config)

    emitted = []
    orchestrator.anomaly_triggered.connect(lambda k, d: emitted.append((k, d)))

    res = orchestrator.trigger_terminal_injection("git status")
    assert len(res.splitlines()) <= 4
    assert len(emitted) == 1
    assert emitted[0][0] == "terminal"


def test_auto_typing_payload_is_harmless_and_contextual():
    app = QApplication.instance() or QApplication([])
    config = DaemonConfig(auto_typing_interval_ms=20)
    orchestrator = DaemonOrchestrator(config=config)
    payload = orchestrator.trigger_auto_typing()

    assert payload
    assert len(payload) <= 240
    assert "harmless assignments" in AUTO_TYPING_SYSTEM_PROMPT
    assert "The user is away" in build_auto_typing_prompt("Code", "code.exe", 20)
    assert orchestrator._ghost_terminal.isVisible()
    assert orchestrator._ghost_terminal.editor.toPlainText().startswith("ghost@daemon:~$ ")

    orchestrator.stop()


def test_ghost_terminal_types_one_character_per_tick():
    app = QApplication.instance() or QApplication([])
    window = GhostTerminalWindow("abc", interval_ms=20)
    window.start_typing()

    assert window.editor.toPlainText() == "ghost@daemon:~$ "
    window._type_next_character()
    assert window.editor.toPlainText().endswith("a")
    window.close()


def test_dashboard_terminal_injection():
    app = QApplication.instance() or QApplication([])
    config = DaemonConfig()
    dashboard = DaemonDashboard(config=config)

    dashboard.txt_term_cmd.setText("python -v")
    dashboard._manual_terminal_injection()

    log_text = dashboard.log_view.toPlainText()
    assert "Terminal Command: 'python -v'" in log_text

    dashboard.close()
