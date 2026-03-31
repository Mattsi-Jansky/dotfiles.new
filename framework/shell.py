import subprocess
import sys
from dataclasses import dataclass

DIM = "\033[2m"
RESET = "\033[0m"


@dataclass
class ShellResult:
    success: bool
    output: str  # combined stdout + stderr


def run_interactive(command: str, label: str = "Interactive") -> ShellResult:
    """Run a command interactively with full TTY access.

    Prints dimmed headers before and after to visually separate the
    interactive output from the framework's own output.
    """
    tty = sys.stdout.isatty()

    if tty:
        sys.stdout.write("\n")
        print(f"  {DIM}── {label} {'─' * max(0, 43 - len(label))}─{RESET}")
        sys.stdout.flush()

    result = subprocess.run(command, shell=True)

    if tty:
        print(f"  {DIM}{'─' * 48}{RESET}")
        sys.stdout.flush()

    return ShellResult(success=(result.returncode == 0), output="")


def run(command: str, stdin: str | None = None) -> ShellResult:
    try:
        proc = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            input=stdin,
        )
        if proc.returncode == 0:
            return ShellResult(success=True, output=proc.stdout + proc.stderr)
        else:
            return ShellResult(success=False, output=proc.stdout + proc.stderr)
    except Exception as e:
        return ShellResult(success=False, output=str(e))
