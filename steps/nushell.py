from framework import runner
from framework.result import Result
from framework.providers.cargo import cargo_install


# Nushell is deliberately NOT set as the login shell: GNOME on Wayland starts
# the desktop session through the login shell, and things that run commands
# via $SHELL expect POSIX syntax. Ghostty launches nu directly instead (see
# config/ghostty/config.ghostty).


@runner.step(group="Nushell", name="Install Nushell")
def install_nushell() -> Result:
    return cargo_install("nu")


@runner.step(group="Nushell", name="Install zoxide")
def install_zoxide() -> Result:
    return cargo_install("zoxide")
