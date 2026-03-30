from unittest.mock import patch, call

from framework.runner import Runner, StepOutcome
from framework.shell import ShellResult

P = "framework.providers.apt"


def _outcomes(runner):
    return [e for e in runner.run_all() if isinstance(e, StepOutcome)]


@patch(f"{P}.clear_pending_line")
def test_all_already_installed(_clear):
    r = Runner()
    with patch(f"{P}.runner", r):
        from framework.providers.apt import install_apt_packages
        install_apt_packages("G", ["curl", "git"])

    with patch(f"{P}.run") as mock_run:
        # dpkg -s succeeds for both
        mock_run.return_value = ShellResult(success=True, output="")
        outcomes = _outcomes(r)

    result = outcomes[0].result
    assert result.status == "skipped"
    assert all(item.status == "skipped" for item in result.items)
    assert len(result.items) == 2


@patch(f"{P}.clear_pending_line")
def test_installs_missing_packages(_clear):
    r = Runner()
    with patch(f"{P}.runner", r):
        from framework.providers.apt import install_apt_packages
        install_apt_packages("G", ["ripgrep", "curl"])

    call_count = 0

    def mock_run_side_effect(cmd, **kwargs):
        nonlocal call_count
        if cmd == "dpkg -s ripgrep":
            call_count += 1
            if call_count == 1:
                return ShellResult(success=False, output="not installed")
            return ShellResult(success=True, output="installed")
        if cmd == "dpkg -s curl":
            return ShellResult(success=True, output="installed")
        if cmd.startswith("sudo apt install"):
            assert "ripgrep" in cmd
            assert "curl" not in cmd  # curl already installed
            return ShellResult(success=True, output="")
        return ShellResult(success=False, output="")

    with patch(f"{P}.run", side_effect=mock_run_side_effect):
        outcomes = _outcomes(r)

    result = outcomes[0].result
    assert result.status == "ok"
    items_by_name = {i.name: i.status for i in result.items}
    assert items_by_name["ripgrep"] == "ok"
    assert items_by_name["curl"] == "skipped"


@patch(f"{P}.clear_pending_line")
def test_failed_install(_clear):
    r = Runner()
    with patch(f"{P}.runner", r):
        from framework.providers.apt import install_apt_packages
        install_apt_packages("G", ["badpkg"])

    def mock_run_side_effect(cmd, **kwargs):
        if cmd == "dpkg -s badpkg":
            return ShellResult(success=False, output="not installed")
        if cmd.startswith("sudo apt install"):
            return ShellResult(success=False, output="failed")
        return ShellResult(success=False, output="")

    with patch(f"{P}.run", side_effect=mock_run_side_effect):
        outcomes = _outcomes(r)

    result = outcomes[0].result
    assert result.status == "failed"
    assert result.items[0].status == "failed"
