import shutil

from framework import runner
from framework.result import Result, ItemResult, ok, skipped, failed
from framework.shell import run
from framework.providers.symlinks import symlink_dotfiles, Dotfile


@runner.step(group="VSCode", name="Install VS Code")
def install_vscode() -> Result:
    if shutil.which("code"):
        result = run("sudo apt install --only-upgrade -y code")
        if result.success and "newly installed" not in result.output and "upgraded" not in result.output:
            return skipped("up to date")
        return ok("updated") if result.success else failed(result.output)

    commands = [
        "sudo apt-get install -y wget gpg",
        "wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor --yes -o /tmp/microsoft.gpg",
        "sudo install -D -o root -g root -m 644 /tmp/microsoft.gpg /usr/share/keyrings/microsoft.gpg",
        "rm -f /tmp/microsoft.gpg",
        'echo "Types: deb\nURIs: https://packages.microsoft.com/repos/code\nSuites: stable\nComponents: main\nArchitectures: amd64,arm64,armhf\nSigned-By: /usr/share/keyrings/microsoft.gpg" | sudo tee /etc/apt/sources.list.d/vscode.sources > /dev/null',
        "sudo apt-get install -y apt-transport-https",
        "sudo apt update",
        "sudo apt install -y code",
    ]

    for cmd in commands:
        result = run(cmd)
        if not result.success:
            return failed(result.output)

    return ok()


symlink_dotfiles("VSCode", [
    Dotfile("config/vscode/settings.json",    "~/.config/Code/User/settings.json"),
    Dotfile("config/vscode/keybindings.json", "~/.config/Code/User/keybindings.json"),
])

EXTENSIONS = [
    "eamodio.gitlens",
    "vscode-icons-team.vscode-icons",
    "davidanson.vscode-markdownlint",
    "anthropic.claude-code",
    "ms-python.vscode-pylance",
    "mathematic.vscode-latex",
    "thenuprojectcontributors.vscode-nushell-lang",
]


@runner.step(group="VSCode", name="extensions")
def install_extensions():
    installed = run("code --list-extensions")
    installed_set = set(installed.output.lower().splitlines()) if installed.success else set()

    for ext in EXTENSIONS:
        if ext.lower() in installed_set:
            yield ItemResult(name=ext, status="skipped")
            continue

        result = run(f"code --install-extension {ext} --force")
        if result.success:
            yield ItemResult(name=ext, status="ok")
        else:
            yield ItemResult(name=ext, status="failed", message=result.output)
