import shutil

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run


@runner.step(group="Rust", name="Install Rust")
def install_rust() -> Result:
    if shutil.which("cargo"):
        return skipped("already installed")
    result = run("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y")
    return ok() if result.success else failed(result.output)
