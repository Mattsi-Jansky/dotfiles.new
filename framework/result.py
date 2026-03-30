from dataclasses import dataclass, field
from typing import Literal

Status = Literal["ok", "skipped", "failed"]


@dataclass
class ItemResult:
    name: str
    status: Status
    message: str = ""


@dataclass
class Result:
    status: Status
    message: str = ""
    items: list[ItemResult] = field(default_factory=list)


def ok(message: str = "", items: list[ItemResult] | None = None) -> Result:
    return Result(status="ok", message=message, items=items or [])


def skipped(message: str = "", items: list[ItemResult] | None = None) -> Result:
    return Result(status="skipped", message=message, items=items or [])


def failed(message: str = "", items: list[ItemResult] | None = None) -> Result:
    return Result(status="failed", message=message, items=items or [])
