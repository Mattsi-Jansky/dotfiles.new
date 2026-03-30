import shutil

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run


@runner.step(group="Starship", name="Install Starship")
def install_starship() -> Result:
    if shutil.which("starship"):
        return skipped("already installed")
    result = run("curl -sS https://starship.rs/install.sh | sh -s -- -y")
    return ok() if result.success else failed(result.output)
