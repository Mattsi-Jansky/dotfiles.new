import os
import shutil

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run


@runner.step(group="Rust", name="Install Rust")
def install_rust() -> Result:
    if shutil.which("cargo"):
        return skipped("already installed")
    result = run("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y")
    if result.success:
        # Make cargo available to subsequent steps in this run
        cargo_bin = os.path.expanduser("~/.cargo/bin")
        if cargo_bin not in os.environ.get("PATH", ""):
            os.environ["PATH"] = f"{cargo_bin}:{os.environ.get('PATH', '')}"
        return ok()
    return failed(result.output)
