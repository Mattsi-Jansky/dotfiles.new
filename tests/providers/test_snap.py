from unittest.mock import patch

from framework.runner import Runner, StepOutcome
from framework.shell import ShellResult
from framework.providers.snap import SnapPackage


def _outcomes(runner):
    return [e for e in runner.run_all() if isinstance(e, StepOutcome)]


def test_all_already_installed():
    r = Runner()
    with patch("framework.providers.snap.runner", r):
        from framework.providers.snap import install_snap_packages
        install_snap_packages("G", [SnapPackage("nvim"), SnapPackage("slack")])

    with patch("framework.providers.snap.run") as mock_run:
        mock_run.return_value = ShellResult(success=True, output="")
        outcomes = _outcomes(r)

    result = outcomes[0].result
    assert result.status == "skipped"
    assert all(item.status == "skipped" for item in result.items)


def test_classic_flag_applied():
    r = Runner()
    with patch("framework.providers.snap.runner", r):
        from framework.providers.snap import install_snap_packages
        install_snap_packages("G", [SnapPackage("nvim", classic=True)])

    commands = []

    def mock_run(cmd):
        commands.append(cmd)
        if cmd.startswith("snap list"):
            return ShellResult(success=False, output="")
        return ShellResult(success=True, output="")

    with patch("framework.providers.snap.run", side_effect=mock_run):
        _outcomes(r)

    install_cmds = [c for c in commands if "install" in c]
    assert any("--classic" in c for c in install_cmds)


def test_partial_failure():
    r = Runner()
    with patch("framework.providers.snap.runner", r):
        from framework.providers.snap import install_snap_packages
        install_snap_packages("G", [SnapPackage("good"), SnapPackage("bad")])

    def mock_run(cmd):
        if cmd == "snap list good":
            return ShellResult(success=False, output="")
        if cmd == "snap list bad":
            return ShellResult(success=False, output="")
        if "good" in cmd and "install" in cmd:
            return ShellResult(success=True, output="")
        if "bad" in cmd and "install" in cmd:
            return ShellResult(success=False, output="error")
        return ShellResult(success=False, output="")

    with patch("framework.providers.snap.run", side_effect=mock_run):
        outcomes = _outcomes(r)

    result = outcomes[0].result
    assert result.status == "failed"
    items_by_name = {i.name: i.status for i in result.items}
    assert items_by_name["good"] == "ok"
    assert items_by_name["bad"] == "failed"
