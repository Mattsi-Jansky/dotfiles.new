from dataclasses import dataclass

from framework import runner
from framework.result import ItemResult
from framework.shell import run


@dataclass
class SnapPackage:
    name: str
    classic: bool = False


def install_snap_packages(group: str, packages: list[SnapPackage],
                          skip_in_test: bool = False) -> None:
    @runner.step(group=group, name="snap packages", skip_in_test=skip_in_test)
    def _snap_step():
        for pkg in packages:
            check = run(f"snap list {pkg.name}")
            if check.success:
                yield ItemResult(name=pkg.name, status="skipped")
                continue

            cmd = f"sudo snap install {pkg.name}"
            if pkg.classic:
                cmd += " --classic"
            install_result = run(cmd)

            if install_result.success:
                yield ItemResult(name=pkg.name, status="ok")
            else:
                yield ItemResult(name=pkg.name, status="failed", message=install_result.output)
