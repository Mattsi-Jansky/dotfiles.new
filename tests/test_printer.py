import io
from unittest.mock import patch, MagicMock

from framework.runner import StepStarted, ItemOutcome, StepOutcome, StepEvent
from framework.result import Result, ItemResult
from framework.printer import print_results, print_summary


def _to_events(outcomes: list[StepOutcome]) -> list[StepEvent]:
    """Convert a list of outcomes into a started/outcome event stream."""
    events: list[StepEvent] = []
    for o in outcomes:
        events.append(StepStarted(group=o.group, name=o.name))
        for item in o.result.items:
            events.append(ItemOutcome(item=item))
        events.append(o)
    return events


def _capture_results(outcomes, is_tty=True):
    events = _to_events(outcomes)
    buf = io.StringIO()
    mock_stdout = MagicMock()
    mock_stdout.write = buf.write
    mock_stdout.flush = MagicMock()
    with patch("framework.printer._is_tty", return_value=is_tty), \
         patch("framework.printer.sys.stdout", mock_stdout), \
         patch("builtins.print", side_effect=lambda *a, **kw: buf.write(" ".join(str(x) for x in a) + "\n")):
        print_results(events)
    return buf.getvalue()


def _capture_summary(outcomes, is_tty=True):
    buf = io.StringIO()
    with patch("framework.printer._is_tty", return_value=is_tty), \
         patch("builtins.print", side_effect=lambda *a, **kw: buf.write(" ".join(str(x) for x in a) + "\n")):
        print_summary(outcomes)
    return buf.getvalue()


def test_group_header():
    output = _capture_results([StepOutcome("MyGroup", "step1", Result("ok", "done"))])
    assert "── MyGroup " in output
    assert "─" * 5 in output


def test_standard_step_with_message():
    output = _capture_results([StepOutcome("G", "Install thing", Result("ok", "installed"))])
    assert "✅" in output
    assert "Install thing" in output
    assert "installed" in output


def test_skipped_step():
    output = _capture_results([StepOutcome("G", "Check", Result("skipped", "already done"))])
    assert "⏭️" in output
    assert "already done" in output


def test_failed_step():
    output = _capture_results([StepOutcome("G", "Bad", Result("failed", "error msg"))])
    assert "❌" in output
    assert "error msg" in output


def test_sub_items_rendering():
    items = [
        ItemResult("ripgrep", "ok"),
        ItemResult("bat", "failed"),
        ItemResult("fzf", "skipped"),
    ]
    output = _capture_results([StepOutcome("Tools", "apt packages", Result("failed", items=items))])
    assert "apt packages" in output
    assert "ripgrep" in output
    assert "bat" in output
    assert "fzf" in output


def test_ascii_icons_when_not_tty():
    outcomes = [
        StepOutcome("G", "ok step", Result("ok")),
        StepOutcome("G", "skip step", Result("skipped")),
        StepOutcome("G", "fail step", Result("failed")),
    ]
    output = _capture_results(outcomes, is_tty=False)
    assert "[ok]" in output
    assert "[--]" in output
    assert "[!!]" in output
    assert "✅" not in output


def test_emoji_icons_when_tty():
    outcomes = [
        StepOutcome("G", "ok step", Result("ok")),
        StepOutcome("G", "skip step", Result("skipped")),
        StepOutcome("G", "fail step", Result("failed")),
    ]
    output = _capture_results(outcomes, is_tty=True)
    assert "✅" in output
    assert "⏭️" in output
    assert "❌" in output


def test_summary_line():
    outcomes = [
        StepOutcome("G", "a", Result("ok")),
        StepOutcome("G", "b", Result("ok")),
        StepOutcome("G", "c", Result("skipped")),
        StepOutcome("H", "d", Result("failed")),
    ]
    output = _capture_summary(outcomes)
    assert "2 ok" in output
    assert "1 skipped" in output
    assert "1 failed" in output


def test_multiple_groups_ordered():
    outcomes = [
        StepOutcome("First", "a", Result("ok")),
        StepOutcome("Second", "b", Result("ok")),
    ]
    output = _capture_results(outcomes)
    first_pos = output.index("First")
    second_pos = output.index("Second")
    assert first_pos < second_pos


@patch("framework.printer.sys.stdout", new_callable=MagicMock)
@patch("framework.printer._is_tty", return_value=False)
@patch("builtins.print")
def test_print_results_returns_all_outcomes(_print, _tty, _stdout):
    events = _to_events([
        StepOutcome("G", "a", Result("ok")),
        StepOutcome("G", "b", Result("failed")),
    ])
    result = print_results(events)
    assert len(result) == 2
    assert result[0].name == "a"
    assert result[1].name == "b"


def test_pending_icon_shown_on_tty():
    output = _capture_results([StepOutcome("G", "Slow step", Result("ok"))])
    assert "✅" in output
    assert "Slow step" in output
