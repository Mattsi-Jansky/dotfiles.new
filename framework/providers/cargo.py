from framework.result import Result, ok, skipped, failed
from framework.shell import run


def cargo_install(crate: str) -> Result:
    """Run cargo install and detect whether it installed, skipped, or failed."""
    result = run(f"cargo install {crate}")
    if not result.success:
        return failed(result.output)
    if "Ignored" in result.output:
        return skipped("up to date")
    return ok("installed")
