from unittest.mock import patch, MagicMock
from pathlib import Path

from framework.runner import Runner, StepOutcome
from framework.providers.symlinks import Dotfile, REPO_ROOT

P = "framework.providers.symlinks"


def _outcomes(runner):
    return [e for e in runner.run_all() if isinstance(e, StepOutcome)]


def _make_runner(dotfile=None):
    r = Runner()
    if dotfile is None:
        dotfile = Dotfile("home/.zshrc", "~/.zshrc")
    with patch(f"{P}.runner", r):
        from framework.providers.symlinks import symlink_dotfiles
        symlink_dotfiles("G", [dotfile])
    return r


def _mock_target(is_symlink=False, exists=False):
    mock = MagicMock()
    mock.is_symlink.return_value = is_symlink
    mock.exists.return_value = exists
    mock.parent = MagicMock()
    return mock


@patch(f"{P}.REPO_ROOT", REPO_ROOT)
@patch(f"{P}.os.readlink", return_value=str(REPO_ROOT / "home/.zshrc"))
@patch(f"{P}.os.path.expanduser", return_value="/home/user/.zshrc")
@patch(f"{P}.Path")
def test_already_linked_skips(MockPath, _expand, _readlink):
    r = _make_runner()
    MockPath.return_value = _mock_target(is_symlink=True, exists=True)
    MockPath.__truediv__ = Path.__truediv__

    outcomes = _outcomes(r)
    assert outcomes[0].result.status == "skipped"
    assert "already linked" in outcomes[0].result.message


@patch(f"{P}.os.symlink")
@patch(f"{P}.os.remove")
@patch(f"{P}.os.readlink", return_value="/wrong/path")
@patch(f"{P}.os.path.expanduser", return_value="/home/user/.zshrc")
@patch(f"{P}.Path")
def test_wrong_target_relinks(MockPath, _expand, _readlink, mock_remove, mock_symlink):
    r = _make_runner()
    MockPath.return_value = _mock_target(is_symlink=True, exists=True)

    outcomes = _outcomes(r)
    assert outcomes[0].result.status == "ok"
    assert "linked" in outcomes[0].result.message
    mock_remove.assert_called_once()
    mock_symlink.assert_called_once()


@patch(f"{P}.os.path.expanduser", return_value="/home/user/.zshrc")
@patch(f"{P}.Path")
def test_real_file_blocks(MockPath, _expand):
    r = _make_runner()
    MockPath.return_value = _mock_target(is_symlink=False, exists=True)

    outcomes = _outcomes(r)
    assert outcomes[0].result.status == "failed"
    assert "not a symlink" in outcomes[0].result.message


@patch(f"{P}.os.symlink")
@patch(f"{P}.os.path.expanduser", return_value="/home/user/.zshrc")
@patch(f"{P}.Path")
def test_new_symlink_created(MockPath, _expand, mock_symlink):
    r = _make_runner()
    mock_target = _mock_target(is_symlink=False, exists=False)
    MockPath.return_value = mock_target

    outcomes = _outcomes(r)
    assert outcomes[0].result.status == "ok"
    assert "linked" in outcomes[0].result.message
    mock_target.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_symlink.assert_called_once()
