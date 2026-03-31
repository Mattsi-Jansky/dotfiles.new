import os
from dataclasses import dataclass
from typing import Callable, Iterator, Union

from framework.result import Result, failed, skipped


@dataclass
class StepStarted:
    group: str
    name: str


@dataclass
class StepOutcome:
    group: str
    name: str
    result: Result


StepEvent = Union[StepStarted, StepOutcome]


class Runner:
    def __init__(self) -> None:
        self._steps: list[tuple[str, str, bool, Callable[[], Result]]] = []

    def step(self, group: str, name: str, interactive: bool = False,
             skip_in_test: bool = False) -> Callable:
        def decorator(fn: Callable[[], Result]) -> Callable[[], Result]:
            self._steps.append((group, name, interactive or skip_in_test, fn))
            return fn
        return decorator

    def run_all(self) -> Iterator[StepEvent]:
        test_mode = os.environ.get("DOTFILES_TEST_MODE") == "1"
        for group, name, skip_in_test, fn in self._steps:
            yield StepStarted(group=group, name=name)
            if test_mode and skip_in_test:
                result = skipped("skipped in test mode")
            else:
                try:
                    result = fn()
                except Exception as e:
                    result = failed(str(e))
            yield StepOutcome(group=group, name=name, result=result)
