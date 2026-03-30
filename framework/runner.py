from dataclasses import dataclass
from typing import Callable, Iterator, Union

from framework.result import Result, failed


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
        self._steps: list[tuple[str, str, Callable[[], Result]]] = []

    def step(self, group: str, name: str) -> Callable:
        def decorator(fn: Callable[[], Result]) -> Callable[[], Result]:
            self._steps.append((group, name, fn))
            return fn
        return decorator

    def run_all(self) -> Iterator[StepEvent]:
        for group, name, fn in self._steps:
            yield StepStarted(group=group, name=name)
            try:
                result = fn()
            except Exception as e:
                result = failed(str(e))
            yield StepOutcome(group=group, name=name, result=result)
