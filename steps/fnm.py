from framework import runner
from framework.result import Result
from framework.providers.cargo import cargo_install


@runner.step(group="fnm", name="Install fnm")
def install_fnm() -> Result:
    return cargo_install("fnm")
