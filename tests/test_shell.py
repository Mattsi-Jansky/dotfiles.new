from unittest.mock import patch, MagicMock
import subprocess

from framework.shell import run


def test_successful_command():
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "hello"
    mock_result.stderr = ""

    with patch("framework.shell.subprocess.run", return_value=mock_result) as mock_run:
        result = run("echo hello")

    mock_run.assert_called_once_with("echo hello", shell=True, capture_output=True, text=True)
    assert result.success is True
    assert result.output == "hello"


def test_failed_command():
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "not found"

    with patch("framework.shell.subprocess.run", return_value=mock_result):
        result = run("false")

    assert result.success is False
    assert result.output == "not found"


def test_exception_in_subprocess():
    with patch("framework.shell.subprocess.run", side_effect=OSError("no such command")):
        result = run("nonexistent")

    assert result.success is False
    assert "no such command" in result.output


def test_combined_stdout_stderr():
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "out"
    mock_result.stderr = "err"

    with patch("framework.shell.subprocess.run", return_value=mock_result):
        result = run("cmd")

    assert result.output == "outerr"
