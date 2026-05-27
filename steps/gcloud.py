import shutil

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run


@runner.step(group="GCloud", name="Install GCloud CLI")
def install_gcloud() -> Result:
    if shutil.which("gcloud"):
        result = run("sudo apt install --only-upgrade -y google-cloud-cli")
        if result.success and "newly installed" not in result.output and "upgraded" not in result.output:
            return skipped("up to date")
        return ok("updated") if result.success else failed(result.output)

    commands = [
        "sudo apt install -y apt-transport-https ca-certificates gnupg curl",
        "curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg",
        'echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list > /dev/null',
        "sudo apt update",
        "sudo apt install -y google-cloud-cli",
    ]

    for cmd in commands:
        result = run(cmd)
        if not result.success:
            return failed(result.output)

    return ok()
