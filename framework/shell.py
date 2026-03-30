import subprocess
from dataclasses import dataclass


@dataclass
class ShellResult:
    success: bool
    output: str  # combined stdout + stderr


def run(command: str, passthrough: bool = False) -> ShellResult:
    try:
        if passthrough:
            proc = subprocess.run(command, shell=True)
            return ShellResult(success=proc.returncode == 0, output="")
        proc = subprocess.run(
            command, shell=True, capture_output=True, text=True
        )
        if proc.returncode == 0:
            return ShellResult(success=True, output=proc.stdout + proc.stderr)
        else:
            return ShellResult(success=False, output=proc.stdout + proc.stderr)
    except Exception as e:
        return ShellResult(success=False, output=str(e))
