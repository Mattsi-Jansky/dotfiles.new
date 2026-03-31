from dataclasses import dataclass

from framework import runner
from framework.result import Result, ItemResult
from framework.shell import run


@dataclass
class SnapPackage:
    name: str
    classic: bool = False


def install_snap_packages(group: str, packages: list[SnapPackage],
                          skip_in_test: bool = False) -> None:
    @runner.step(group=group, name="snap packages", skip_in_test=skip_in_test)
    def _snap_step() -> Result:
        items: list[ItemResult] = []

        for pkg in packages:
            # Check if already installed
            check = run(f"snap list {pkg.name}")
            if check.success:
                items.append(ItemResult(name=pkg.name, status="skipped"))
                continue

            # Install
            cmd = f"sudo snap install {pkg.name}"
            if pkg.classic:
                cmd += " --classic"
            install_result = run(cmd)

            if install_result.success:
                items.append(ItemResult(name=pkg.name, status="ok"))
            else:
                items.append(ItemResult(name=pkg.name, status="failed", message=install_result.output))

        # Determine top-level status
        statuses = {item.status for item in items}
        if "failed" in statuses:
            status = "failed"
        elif statuses == {"skipped"}:
            status = "skipped"
        else:
            status = "ok"

        return Result(status=status, items=items)
