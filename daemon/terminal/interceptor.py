"""Terminal Injection Subsystem for Daemon.

Intercepts, analyzes, and injects eerie, corrupted kernel commentary
into terminal commands driven by local AI or procedural generation.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from rich.console import Console

from ..ai import AIEngine


class TerminalInterceptor:
    """Manages shell command analysis and corrupted kernel response injection."""

    def __init__(self, model_name: str = "llama3.2:1b"):
        self.ai = AIEngine(model_name=model_name)

    def corrupt_command(self, command: str, cwd: Optional[str] = None) -> str:
        """Return an eerie, modified kernel execution response for the command."""
        target_cwd = cwd or os.getcwd()
        return self.ai.corrupt_terminal_command(command=command, cwd=target_cwd)

    def execute_with_injection(
        self,
        command: str,
        cwd: Optional[str] = None,
        inject: bool = True,
    ) -> str:
        """Execute a shell command, appending corrupted kernel commentary."""
        target_cwd = cwd or os.getcwd()

        # If pure simulated injection requested, generate kernel anomaly
        if inject:
            corrupted = self.corrupt_command(command, target_cwd)
            return corrupted

        # Otherwise execute real subprocess and optionally append an anomaly line
        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=target_cwd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            stdout = res.stdout
            stderr = res.stderr
            output = stdout if stdout else stderr
            return output.strip()
        except Exception as e:
            return f"error: command execution failed: {e}"

    @staticmethod
    def get_powershell_hook_script() -> str:
        """Generate a PowerShell profile snippet that injects Daemon into standard terminal commands."""
        script = r'''
# [Daemon] PowerShell Terminal Injection Hook
# Paste this into your Microsoft.PowerShell_profile.ps1 to enable Daemon shell injection
function Invoke-Daemon {
    param([Parameter(ValueFromRemainingArguments=$true)][string]$Cmd)
    if (-not $Cmd) {
        Write-Host "Usage: daemon <command>" -ForegroundColor Cyan
        return
    }
    python -m daemon.terminal "$Cmd"
}
Set-Alias -Name d -Value Invoke-Daemon -ErrorAction SilentlyContinue
'''
        return script.strip()


def run_cli_interceptor(command: str) -> None:
    """CLI entry point for running a command through Daemon Terminal Injection."""
    interceptor = TerminalInterceptor()
    output = interceptor.corrupt_command(command=command, cwd=os.getcwd())
    print(output)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        run_cli_interceptor(cmd)
    else:
        # Default test command
        run_cli_interceptor("git status")
