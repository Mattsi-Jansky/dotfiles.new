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


@runner.step(group="Docker", name="Docker group")
def docker_group() -> Result:
    result = run("getent group docker")
    if not result.success:
        create = run("sudo groupadd -f docker")
        if not create.success:
            return failed(create.output)

    import getpass
    user = getpass.getuser()
    check = run(f"id -nG {user}")
    if "docker" in check.output.split():
        return skipped("already in group")

    result = run(f"sudo usermod -aG docker {user}")
    return ok("added to docker group") if result.success else failed(result.output)
