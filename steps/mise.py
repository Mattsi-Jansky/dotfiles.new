import os
import shutil

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run


@runner.step(group="mise", name="Install mise")
def install_mise() -> Result:
    if shutil.which("mise"):
        return skipped("already installed")
    result = run("curl https://mise.run | sh")
    if not result.success:
        return failed(result.output)
    local_bin = os.path.expanduser("~/.local/bin")
    if local_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{local_bin}:{os.environ.get('PATH', '')}"
    return ok()


def _java_installed(version: str) -> bool:
    result = run("mise ls --installed java")
    if not result.success:
        return False
    prefix = f"{version}."
    for line in result.output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] == "java" and parts[1].startswith(prefix):
            return True
    return False


def _install_java(version: str) -> Result:
    if not shutil.which("mise"):
        return failed("mise not installed")
    if _java_installed(version):
        return skipped("already installed")
    result = run(f"mise install java@{version}")
    return ok() if result.success else failed(result.output)


@runner.step(group="mise", name="Install Java 11")
def install_java_11() -> Result:
    return _install_java("11")


@runner.step(group="mise", name="Install Java 17")
def install_java_17() -> Result:
    return _install_java("17")


@runner.step(group="mise", name="Install Java 21")
def install_java_21() -> Result:
    return _install_java("21")


@runner.step(group="mise", name="Install Java 25")
def install_java_25() -> Result:
    return _install_java("25")
