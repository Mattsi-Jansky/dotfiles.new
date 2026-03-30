import getpass
import shutil

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run
from framework.providers.cargo import cargo_install


@runner.step(group="Nushell", name="Install Nushell")
def install_nushell() -> Result:
    return cargo_install("nu")


@runner.step(group="Nushell", name="Install zoxide")
def install_zoxide() -> Result:
    return cargo_install("zoxide")


@runner.step(group="Nushell", name="Set default shell")
def set_default_shell() -> Result:
    nu_path = shutil.which("nu")
    if not nu_path:
        return failed("nu not found in PATH")

    # Check if already the default shell
    check = run("getent passwd $USER")
    if check.success and check.output.strip().endswith(nu_path):
        return skipped("already default")

    password = getpass.getpass(prompt="\n  [sudo] password for default shell: ")

    # Ensure nu is in /etc/shells
    shells_check = run(f"grep -qx '{nu_path}' /etc/shells")
    if not shells_check.success:
        add = run(f"sudo -S tee -a /etc/shells", stdin=f"{password}\n{nu_path}\n")
        if not add.success:
            return failed(add.output)

    result = run(f"sudo -S chsh -s {nu_path} $USER", stdin=f"{password}\n")
    return ok("set as default") if result.success else failed(result.output)
