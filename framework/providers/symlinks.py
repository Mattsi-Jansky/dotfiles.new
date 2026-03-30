import os
from dataclasses import dataclass
from pathlib import Path

from framework import runner
from framework.result import Result, ok, skipped, failed

# Repo root: directory containing main.py (parent of framework/)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class Dotfile:
    source: str  # relative path within the repo, e.g. "home/.zshrc"
    target: str  # path on the filesystem, e.g. "~/.zshrc" (~ is expanded)


def symlink_dotfiles(group: str, dotfiles: list[Dotfile]) -> None:
    for dotfile in dotfiles:
        @runner.step(group=group, name=dotfile.target)
        def _symlink_step(_df: Dotfile = dotfile) -> Result:
            target = Path(os.path.expanduser(_df.target))
            source = REPO_ROOT / _df.source

            if target.is_symlink():
                if os.readlink(target) == str(source):
                    return skipped("already linked")
                else:
                    os.remove(target)
                    os.symlink(source, target)
                    return ok("relinked")
            elif target.exists():
                return failed("target exists and is not a symlink")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                os.symlink(source, target)
                return ok("linked")
