import getpass
import shutil

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run


@runner.step(group="Docker", name="Install Docker")
def install_docker() -> Result:
    if shutil.which("docker"):
        result = run("sudo apt install --only-upgrade -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin")
        if result.success and "newly installed" not in result.output and "upgraded" not in result.output:
            return skipped("up to date")
        return ok("updated") if result.success else failed(result.output)

    commands = [
        "sudo apt install -y ca-certificates curl",
        "sudo install -m 0755 -d /etc/apt/keyrings",
        "sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc",
        "sudo chmod a+r /etc/apt/keyrings/docker.asc",
        'echo "Types: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: $(. /etc/os-release && echo ${UBUNTU_CODENAME:-$VERSION_CODENAME})\nComponents: stable\nArchitectures: $(dpkg --print-architecture)\nSigned-By: /etc/apt/keyrings/docker.asc" | sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null',
        "sudo apt update",
        "sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
    ]

    for cmd in commands:
        result = run(cmd)
        if not result.success:
            return failed(result.output)

    return ok()


@runner.step(group="Docker", name="Docker group")
def docker_group() -> Result:
    user = getpass.getuser()
    check = run(f"id -nG {user}")
    if "docker" in check.output.split():
        return skipped("already in group")

    result = run(f"sudo usermod -aG docker {user}")
    return ok("added to docker group") if result.success else failed(result.output)
