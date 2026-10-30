"""Main entry point for Daemon: An AI-Powered Desktop Poltergeist."""

import sys
import signal
import argparse
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from daemon import __version__
from daemon.config import DaemonConfig
from daemon.overlay import OverlayCanvas
from daemon.audio import AudioSynth
from daemon.orchestrator import DaemonOrchestrator
from daemon.ui import DaemonTrayIcon


def print_banner(console: Console, config: DaemonConfig) -> None:
    banner = f"""[bold red]
 👻  D A E M O N  👻
[/bold red][dim]An AI-Powered Desktop Poltergeist v{__version__}[/dim]
[cyan]Presence-aware, system-integrated haunted overlay driven by local AI[/cyan]"""
    console.print(Panel(banner, border_style="red", expand=False))

    table = Table(title="Daemon Configuration", border_style="dim")
    table.add_column("Setting", style="bold cyan")
    table.add_column("Value", style="yellow")

    table.add_row("AI Model", config.model_name)
    table.add_row("Anomaly Threshold", f"{config.anomaly_threshold * 100:.0f}%")
    table.add_row("Audio Synthesis", "Enabled" if config.enable_audio_synth else "Disabled")
    table.add_row("Max Entities", str(config.max_entities))
    table.add_row("Idle Trigger Window", f"{config.idle_threshold_seconds}s")
    table.add_row("Anomaly Cooldown", f"{config.anomaly_cooldown_seconds}s")

    console.print(table)
    console.print("[dim]Running in background. Look for the 👻 icon in your system tray.[/dim]")
    console.print("[dim]Press Ctrl+C in terminal or right-click tray icon to exit.[/dim]\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daemon: An AI-Powered Desktop Poltergeist")
    parser.add_argument("--config", type=str, default="config.json", help="Path to config.json")
    parser.add_argument("--threshold", type=float, help="Override anomaly tension threshold (0.0 - 1.0)")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio synthesis")
    parser.add_argument("--no-overlay", action="store_true", help="Run without transparent visual overlay")
    parser.add_argument("--gui", action="store_true", help="Launch the desktop control center window")
    parser.add_argument("--terminal-inject", type=str, help="Corrupt and execute a terminal command through Daemon")
    parser.add_argument("--powershell-hook", action="store_true", help="Print PowerShell profile integration snippet")
    parser.add_argument("--test-anomaly", choices=["whisper", "crawler", "glitch", "watcher", "terminal"], help="Trigger a test anomaly on startup")
    parser.add_argument("--debug", action="store_true", help="Enable verbose telemetry output in console")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    console = Console()

    # Load configuration
    config = DaemonConfig.load(args.config)
    if args.threshold is not None:
        config.anomaly_threshold = args.threshold
    if args.no_audio:
        config.enable_audio_synth = False
    if args.debug:
        config.debug_mode = True

    # If --terminal-inject is requested, run and output directly
    if args.terminal_inject:
        from daemon.terminal import TerminalInterceptor
        interceptor = TerminalInterceptor(model_name=config.model_name)
        print(interceptor.corrupt_command(args.terminal_inject))
        return 0

    # If --powershell-hook is requested, output hook snippet
    if args.powershell_hook:
        from daemon.terminal.interceptor import TerminalInterceptor
        print(TerminalInterceptor.get_powershell_hook_script())
        return 0

    # If --gui is selected, launch desktop control app
    if args.gui:
        app = QApplication(sys.argv)
        app.setApplicationName("Daemon")
        signal.signal(signal.SIGINT, lambda *_: QApplication.quit())
        sig_timer = QTimer()
        sig_timer.timeout.connect(lambda: None)
        sig_timer.start(500)

        from daemon.ui import DaemonDashboard
        window = DaemonDashboard(config=config)
        window.show()
        return app.exec()

    print_banner(console, config)

    # Initialize Qt Application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Clean Ctrl+C handling in Qt event loop
    signal.signal(signal.SIGINT, lambda *_: QApplication.quit())
    sig_timer = QTimer()
    sig_timer.timeout.connect(lambda: None)
    sig_timer.start(500)

    # Visual overlay canvas
    canvas = None
    if not args.no_overlay:
        canvas = OverlayCanvas(max_entities=config.max_entities)
        canvas.show()

    # Procedural audio synthesizer
    synth = None
    if config.enable_audio_synth:
        synth = AudioSynth(master_volume=config.sound_volume, enabled=True)

    # Central orchestrator
    orchestrator = DaemonOrchestrator(config=config, canvas=canvas, synth=synth)

    # System tray
    tray = None
    if DaemonTrayIcon.isSystemTrayAvailable():
        tray = DaemonTrayIcon(orchestrator=orchestrator)
        tray.show()
    else:
        console.print("[yellow]System tray not available in this environment, running in headless tray mode.[/yellow]")

    # Live telemetry console updates in debug mode or on anomaly
    def on_anomaly(kind: str, detail: str):
        console.print(f"[bold red]► Anomaly Dispatched:[/bold red] [yellow]{kind.upper()}[/yellow] - {detail}")

    orchestrator.anomaly_triggered.connect(on_anomaly)

    # Startup test anomaly if requested
    if args.test_anomaly:
        def run_test():
            if args.test_anomaly == "whisper":
                orchestrator.trigger_whisper()
            elif args.test_anomaly == "crawler":
                orchestrator.trigger_crawler()
            elif args.test_anomaly == "glitch":
                orchestrator.trigger_glitch()
            elif args.test_anomaly == "watcher":
                orchestrator.trigger_watcher()
            elif args.test_anomaly == "terminal":
                orchestrator.trigger_terminal_injection("git status")

        QTimer.singleShot(1000, run_test)

    # Start the daemon
    orchestrator.start()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

