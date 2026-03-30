import shutil

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run


@runner.step(group="GitHub", name="Install GitHub CLI")
def install_gh() -> Result:
    if shutil.which("gh"):
        result = run("sudo apt install --only-upgrade -y gh")
        if result.success and "newly installed" not in result.output and "upgraded" not in result.output:
            return skipped("up to date")
        return ok("updated") if result.success else failed(result.output)

    commands = [
        "sudo mkdir -p -m 755 /etc/apt/keyrings",
        "wget -nv -O /tmp/githubcli-archive-keyring.gpg https://cli.github.com/packages/githubcli-archive-keyring.gpg",
        "sudo mv /tmp/githubcli-archive-keyring.gpg /etc/apt/keyrings/githubcli-archive-keyring.gpg",
        "sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg",
        "sudo mkdir -p -m 755 /etc/apt/sources.list.d",
        'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null',
        "sudo apt update",
        "sudo apt install gh -y",
    ]

    for cmd in commands:
        result = run(cmd)
        if not result.success:
            return failed(result.output)

    return ok()
