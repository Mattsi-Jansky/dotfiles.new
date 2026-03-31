from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run
from framework.providers.snap import install_snap_packages, SnapPackage

install_snap_packages("Snap Tools", [
    SnapPackage("slack"),
    SnapPackage("powershell", classic=True),
    SnapPackage("intellij-idea-ultimate", classic=True),
    SnapPackage("webstorm", classic=True),
    SnapPackage("obsidian", classic=True),
    SnapPackage("spotify", classic=True),
    SnapPackage("gimp"),
], skip_in_test=True)


@runner.step(group="Snap Tools", name="Refresh snaps", skip_in_test=True)
def refresh_snaps() -> Result:
    result = run("sudo snap refresh")
    return ok() if result.success else failed(result.output)
