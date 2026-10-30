"""Command-line entrypoint for python -m daemon.terminal."""

import sys
from .interceptor import run_cli_interceptor

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        run_cli_interceptor(cmd)
    else:
        run_cli_interceptor("git status")

