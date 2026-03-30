from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run
from framework.providers.cargo import cargo_install


@runner.step(group="fnm", name="Install fnm")
def install_fnm() -> Result:
    return cargo_install("fnm")


@runner.step(group="fnm", name="Install Node LTS")
def install_node_lts() -> Result:
    check = run("fnm list")
    if check.success and "lts-latest" in check.output:
        return skipped("already installed")
    result = run("fnm install --lts")
    if not result.success:
        return failed(result.output)
    default = run("fnm default lts-latest")
    return ok() if default.success else failed(default.output)
