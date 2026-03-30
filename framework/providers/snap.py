from dataclasses import dataclass

from framework import runner
from framework.result import Result, ItemResult
from framework.shell import run
from framework.printer import clear_pending_line


@dataclass
class SnapPackage:
    name: str
    classic: bool = False


def install_snap_packages(group: str, packages: list[SnapPackage]) -> None:
    @runner.step(group=group, name="snap packages")
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
            clear_pending_line()
            install_result = run(cmd, passthrough=True)

            if install_result.success:
                items.append(ItemResult(name=pkg.name, status="ok"))
            else:
                items.append(ItemResult(name=pkg.name, status="failed"))

        # Determine top-level status
        statuses = {item.status for item in items}
        if "failed" in statuses:
            status = "failed"
        elif statuses == {"skipped"}:
            status = "skipped"
        else:
            status = "ok"

        return Result(status=status, items=items)
