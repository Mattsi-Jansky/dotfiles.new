from framework import runner
from framework.result import Result, ItemResult
from framework.shell import run


def install_apt_packages(group: str, packages: list[str]) -> None:
    @runner.step(group=group, name="apt packages")
    def _apt_step() -> Result:
        items: list[ItemResult] = []
        already_installed: list[str] = []
        to_install: list[str] = []

        # Check which packages are already installed
        for pkg in packages:
            check = run(f"dpkg -s {pkg}")
            if check.success:
                already_installed.append(pkg)
            else:
                to_install.append(pkg)

        # Install missing packages in one call
        install_output = ""
        if to_install:
            result = run(f"sudo apt install -y {' '.join(to_install)}")
            install_output = result.output

        # Build item results
        for pkg in packages:
            if pkg in already_installed:
                items.append(ItemResult(name=pkg, status="skipped"))
            else:
                verify = run(f"dpkg -s {pkg}")
                if verify.success:
                    items.append(ItemResult(name=pkg, status="ok"))
                else:
                    items.append(ItemResult(name=pkg, status="failed", message=install_output))

        # Determine top-level status
        statuses = {item.status for item in items}
        if "failed" in statuses:
            status = "failed"
        elif statuses == {"skipped"}:
            status = "skipped"
        else:
            status = "ok"

        return Result(status=status, items=items)
