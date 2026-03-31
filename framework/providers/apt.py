from framework import runner
from framework.result import ItemResult
from framework.shell import run


def install_apt_packages(group: str, packages: list[str]) -> None:
    @runner.step(group=group, name="apt packages")
    def _apt_step():
        run("sudo apt update")

        for pkg in packages:
            if run(f"dpkg -s {pkg}").success:
                yield ItemResult(name=pkg, status="skipped")
                continue

            result = run(f"sudo apt install -y {pkg}")
            if result.success:
                yield ItemResult(name=pkg, status="ok")
            else:
                yield ItemResult(name=pkg, status="failed", message=result.output)
