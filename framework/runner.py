import inspect
import os
from dataclasses import dataclass
from typing import Callable, Iterator, Union

from framework.result import Result, ItemResult, failed, skipped


@dataclass
class StepStarted:
    group: str
    name: str


@dataclass
class ItemOutcome:
    item: ItemResult


@dataclass
class StepOutcome:
    group: str
    name: str
    result: Result


StepEvent = Union[StepStarted, ItemOutcome, StepOutcome]


class Runner:
    def __init__(self) -> None:
        self._steps: list[tuple[str, str, bool, Callable]] = []

    def step(self, group: str, name: str, interactive: bool = False,
             skip_in_test: bool = False) -> Callable:
        def decorator(fn: Callable) -> Callable:
            self._steps.append((group, name, interactive or skip_in_test, fn))
            return fn
        return decorator

    def run_all(self) -> Iterator[StepEvent]:
        test_mode = os.environ.get("DOTFILES_TEST_MODE") == "1"
        for group, name, skip_in_test, fn in self._steps:
            yield StepStarted(group=group, name=name)
            if test_mode and skip_in_test:
                yield StepOutcome(group=group, name=name, result=skipped("skipped in test mode"))
                continue

            try:
                ret = fn()
                if inspect.isgenerator(ret):
                    items: list[ItemResult] = []
                    for item in ret:
                        items.append(item)
                        yield ItemOutcome(item=item)

                    statuses = {i.status for i in items}
                    if "failed" in statuses:
                        status = "failed"
                    elif statuses == {"skipped"}:
                        status = "skipped"
                    else:
                        status = "ok"
                    result = Result(status=status, items=items)
                else:
                    result = ret
            except Exception as e:
                result = failed(str(e))
            yield StepOutcome(group=group, name=name, result=result)
