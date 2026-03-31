import shutil

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run
from framework.providers.symlinks import symlink_dotfiles, Dotfile


@runner.step(group="Wezterm", name="Install Wezterm")
def install_wezterm() -> Result:
    if shutil.which("wezterm"):
        result = run("sudo apt install --only-upgrade -y wezterm")
        if result.success and "newly installed" not in result.output and "upgraded" not in result.output:
            return skipped("up to date")
        return ok("updated") if result.success else failed(result.output)

    commands = [
        "curl -fsSL https://apt.fury.io/wez/gpg.key | sudo gpg --yes --dearmor -o /usr/share/keyrings/wezterm-fury.gpg",
        "echo 'deb [signed-by=/usr/share/keyrings/wezterm-fury.gpg] https://apt.fury.io/wez/ * *' | sudo tee /etc/apt/sources.list.d/wezterm.list",
        "sudo chmod 644 /usr/share/keyrings/wezterm-fury.gpg",
        "sudo apt update",
        "sudo apt install -y wezterm",
    ]

    for cmd in commands:
        result = run(cmd)
        if not result.success:
            return failed(result.output)

    return ok()


symlink_dotfiles("Wezterm", [
    Dotfile("config/wezterm/wezterm.lua", "~/.config/wezterm/wezterm.lua"),
])
