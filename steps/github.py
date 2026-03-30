import os
import shutil
import subprocess

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run

SSH_KEY_PATH = os.path.expanduser("~/.ssh/github")


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


@runner.step(group="GitHub", name="Generate SSH key")
def generate_ssh_key() -> Result:
    if os.path.exists(SSH_KEY_PATH):
        return skipped("already exists")

    os.makedirs(os.path.dirname(SSH_KEY_PATH), mode=0o700, exist_ok=True)
    gen = run(f'ssh-keygen -t ed25519 -C "mattsi@jansky.dev" -f {SSH_KEY_PATH} -N ""')
    return ok() if gen.success else failed(gen.output)


@runner.step(group="GitHub", name="Authenticate GitHub CLI")
def authenticate_gh() -> Result:
    auth = run("gh auth status")
    # if auth.success:
    #     return skipped("already authenticated")

    login = subprocess.run(
        "gh auth login --git-protocol ssh --web "
        "--skip-ssh-key --scopes admin:public_key",
        shell=True,
    )
    if login.returncode != 0:
        return failed("gh auth login failed")

    return ok()


@runner.step(group="GitHub", name="Upload SSH key")
def upload_ssh_key() -> Result:
    import socket
    hostname = socket.gethostname()

    # Check if this key is already uploaded
    check = run(f"gh ssh-key list")
    if check.success:
        pub_key = open(f"{SSH_KEY_PATH}.pub").read().split()[1]
        if pub_key in check.output:
            return skipped("already uploaded")

    result = run(f"gh ssh-key add {SSH_KEY_PATH}.pub --title {hostname}")
    return ok(hostname) if result.success else failed(result.output)
