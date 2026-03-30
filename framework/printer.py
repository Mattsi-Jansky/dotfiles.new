import sys
from typing import Iterable

from framework.runner import StepStarted, StepOutcome, StepEvent

RULE_WIDTH = 56

# ANSI colours
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

# Terminal control
CLEAR_LINE = "\033[2K"

EMOJI_ICONS = {"ok": "✅", "skipped": "⏭️", "failed": "❌"}
ASCII_ICONS = {"ok": "[ok]", "skipped": "[--]", "failed": "[!!]"}
PENDING_ICON_EMOJI = "⏳"
PENDING_ICON_ASCII = "[..]"


def _is_tty() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _icon(status: str, tty: bool) -> str:
    if tty:
        return EMOJI_ICONS[status]
    return ASCII_ICONS[status]


def _colour(status: str, text: str, tty: bool) -> str:
    if not tty:
        return text
    colours = {"ok": GREEN, "skipped": YELLOW, "failed": RED}
    return f"{colours[status]}{text}{RESET}"


def _print_group_header(group_name: str) -> None:
    header = f"── {group_name} "
    header += "─" * max(0, RULE_WIDTH - len(header))
    print(header)


def _print_pending(name: str, tty: bool) -> None:
    """Print step name with a pending icon, no newline. On non-TTY, skip."""
    if not tty:
        return
    icon = PENDING_ICON_EMOJI
    sys.stdout.write(f"  {icon}  {name}")
    sys.stdout.flush()


def _clear_pending(tty: bool) -> None:
    """Return to line start and clear it, undoing _print_pending."""
    if not tty:
        return
    sys.stdout.write(f"\r{CLEAR_LINE}")
    sys.stdout.flush()


def clear_pending_line() -> None:
    """Clear the pending status line. Call before passthrough commands."""
    if _is_tty():
        sys.stdout.write(f"\r{CLEAR_LINE}")
        sys.stdout.flush()


def _print_outcome(outcome: StepOutcome, tty: bool) -> None:
    if outcome.result.items:
        print(f"  {outcome.name}")
        for item in outcome.result.items:
            icon = _icon(item.status, tty)
            coloured_icon = _colour(item.status, icon, tty)
            print(f"    {coloured_icon}  {item.name}")
    else:
        icon = _icon(outcome.result.status, tty)
        coloured_icon = _colour(outcome.result.status, icon, tty)
        line = f"  {coloured_icon}  {outcome.name}"
        if outcome.result.message:
            line += f"  {outcome.result.message}"
        print(line)


def print_results(events: Iterable[StepEvent]) -> list[StepOutcome]:
    """Print each step as it starts and finishes. Returns all outcomes for summary."""
    tty = _is_tty()
    current_group = None
    all_outcomes: list[StepOutcome] = []

    for event in events:
        if isinstance(event, StepStarted):
            if event.group != current_group:
                if current_group is not None:
                    print()
                _print_group_header(event.group)
                current_group = event.group
            _print_pending(event.name, tty)

        elif isinstance(event, StepOutcome):
            _clear_pending(tty)
            _print_outcome(event, tty)
            all_outcomes.append(event)

    if current_group is not None:
        print()

    return all_outcomes


def print_summary(outcomes: list[StepOutcome]) -> None:
    ok_count = sum(1 for o in outcomes if o.result.status == "ok")
    skip_count = sum(1 for o in outcomes if o.result.status == "skipped")
    fail_count = sum(1 for o in outcomes if o.result.status == "failed")

    rule = "─" * RULE_WIDTH
    print(rule)
    print(f"  {ok_count} ok  ·  {skip_count} skipped  ·  {fail_count} failed")
