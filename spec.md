# Dotfiles Framework — Python Implementation Spec

## Overview

A lightweight Python framework for deterministic-ish machine configuration. It stores idempotent setup functions, executes them, and pretty-prints grouped results. No external dependencies. Clone the repo and run `python3 main.py`.

---

## Goals

- Zero external dependencies (stdlib only)
- Runnable on a fresh Ubuntu machine with only `git` and `python3` (both present by default)
- Idempotent: safe to run repeatedly; steps should detect and skip already-complete work
- Steps are grouped and results are pretty-printed to the terminal with ANSI colours
- Failing steps must not abort the run; all steps should always be attempted
- The framework and the configuration that uses it live in separate layers

---

## Project Structure

```
dotfiles/
├── framework/
│   ├── __init__.py
│   ├── runner.py        # Step registry, execution, result collection
│   ├── result.py        # Result type definitions
│   ├── shell.py         # Shell execution helpers
│   ├── printer.py       # ANSI output, grouped summary
│   └── providers/
│       ├── __init__.py
│       ├── apt.py       # Batch apt install abstraction
│       ├── snap.py      # Batch snap install abstraction
│       └── symlinks.py  # Home dotfile symlinking abstraction
├── steps/
│   ├── __init__.py
│   ├── shell_tools.py   # e.g. ripgrep, fd, bat, fzf
│   ├── dotfiles.py      # Symlinking config files
│   ├── git.py           # Git global config
│   └── ...              # One file per logical group
├── main.py              # Entrypoint: imports steps, runs runner
└── tests/
    ├── test_runner.py
    ├── test_result.py
    ├── test_shell.py
    ├── test_printer.py
    └── providers/
        ├── test_apt.py
        ├── test_snap.py
        └── test_symlinks.py
```

---

## Result Type

```python
# framework/result.py

from dataclasses import dataclass, field
from typing import Literal

Status = Literal["ok", "skipped", "failed"]

@dataclass
class ItemResult:
    name: str
    status: Status

@dataclass
class Result:
    status: Status
    message: str = ""
    items: list[ItemResult] = field(default_factory=list)

def ok(message: str = "", items: list[ItemResult] = []) -> Result: ...
def skipped(message: str = "", items: list[ItemResult] = []) -> Result: ...
def failed(message: str = "", items: list[ItemResult] = []) -> Result: ...
```

Steps return a `Result`. The `message` is optional and displayed inline for steps without sub-items. When `items` is populated, the printer renders sub-item lines instead of a message. The top-level `status` reflects the overall outcome: `failed` if any item failed, `skipped` if all items were skipped, `ok` otherwise.

---

## Shell Helper

```python
# framework/shell.py

from dataclasses import dataclass

@dataclass
class ShellResult:
    success: bool
    output: str  # combined stdout + stderr

def run(command: str) -> ShellResult: ...
```

- Uses `subprocess.run` with `shell=True`, `capture_output=True`, `text=True`
- Never raises; returns `ShellResult(success=False, output=<stderr>)` on failure

---

## Step Registration

Steps are registered via a decorator provided by the framework. The decorator lives on the `Runner` instance so that multiple runners with different scopes are possible in future.

```python
# Usage example in steps/shell_tools.py

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run
import shutil

@runner.step(group="Shell Tools", name="Install ripgrep")
def install_ripgrep() -> Result:
    if shutil.which("rg"):
        return skipped("already installed")
    result = run("sudo apt install -y ripgrep")
    return ok() if result.success else failed(result.output)
```

- `group` is used to visually group steps in output. Steps with the same `group` string are printed together.
- `name` is the display label for the step.
- The decorated function must return a `Result`.
- Exceptions raised inside a step are caught by the runner and recorded as `failed`.

---

## Runner

```python
# framework/runner.py

class Runner:
    def step(self, group: str, name: str): ...  # decorator factory
    def run_all(self) -> list[StepOutcome]: ...
```

`StepOutcome` is an internal dataclass holding `group`, `name`, and `Result`. The runner:

1. Executes steps in registration order
2. Catches any unhandled exception from a step and converts it to `failed(str(exception))`
3. Never short-circuits on failure
4. Returns all outcomes for the printer to consume

A global `runner` instance is exported from `framework/__init__.py` so steps can import it directly.

---

## Printer

```python
# framework/printer.py

def print_summary(outcomes: list[StepOutcome]) -> None: ...
```

### Icons

Use emoji icons when stdout is a TTY, plain ASCII brackets when piped:

| Status    | Emoji | ASCII  |
|-----------|-------|--------|
| `ok`      | ✅    | `[ok]` |
| `skipped` | ⏭️    | `[--]` |
| `failed`  | ❌    | `[!!]` |

### Output format

Steps without sub-items (standard steps, symlinks):

```
── Dotfiles ─────────────────────────────────────────
  ✅  ~/.zshrc                linked
  ⏭️   ~/.gitconfig            already linked
  ❌  ~/.config/nvim          target exists and is not a symlink
```

Steps with sub-items (apt, snap):

```
── Shell Tools ──────────────────────────────────────
  apt packages
    ✅  ripgrep
    ✅  fd-find
    ❌  bat
    ⏭️   fzf

── Developer Tools ──────────────────────────────────
  snap packages
    ✅  nvim
    ⏭️   slack
    ❌  spotify
```

Rules:
- Group headers use a `──` rule padded to 60 chars
- Standard step rows: two-space indent, icon, step name left-padded to a fixed width, message
- Sub-item header (step name): two-space indent, no icon, plain text
- Sub-item rows: four-space indent, icon, package name — no message column
- `⏭️` (emoji) is wider than other icons; add one extra space after it to keep columns aligned
- ANSI colour is applied to the icon only, not the name or message
- If stdout is not a TTY, strip all ANSI and use ASCII icon set

After all groups, print a one-line summary:

```
────────────────────────────────────────────────────
  3 ok  ·  2 skipped  ·  1 failed
```

The summary counts are over top-level steps, not individual sub-items.

Exit code is `0` if no steps failed, `1` if any step failed.

---

## Entrypoint

```python
# main.py

import steps.shell_tools
import steps.dotfiles
import steps.git

from framework import runner
from framework.printer import print_summary
import sys

if __name__ == "__main__":
    outcomes = runner.run_all()
    print_summary(outcomes)
    sys.exit(0 if all(o.result.status != "failed" for o in outcomes) else 1)
```

Importing a steps module causes its `@runner.step(...)` decorators to execute, which registers the steps. No magic discovery — explicit imports only.

---

## Idempotency Convention

Steps are responsible for their own idempotency. Common patterns:

- **Binary exists**: `shutil.which("rg")`
- **Package installed**: `run("dpkg -s ripgrep").success`
- **File/symlink exists**: `os.path.exists(path)` or `os.path.islink(path)`
- **Symlink points to correct target**: `os.readlink(path) == expected`
- **Line exists in file**: read and check before appending
- **Git config set**: `run("git config --global user.name").output.strip() != ""`

When already done, return `skipped(...)`. When action is taken, return `ok(...)`. When something goes wrong, return `failed(message)`.

---

## Abstractions

The `framework/providers/` module provides higher-level helpers for common setup patterns. Apt and snap providers register a single step that produces per-package sub-item output. Symlinks register one step per file.

### Apt

```python
# framework/providers/apt.py

def install_apt_packages(group: str, packages: list[str]) -> None: ...
```

Registers a single step under the given `group` named `"apt packages"`. When run, it:

1. Checks each package using `dpkg -s <pkg>` to determine which are already installed
2. Installs any missing packages in one `sudo apt install -y <pkg1> <pkg2> ...` call
3. Returns a `Result` whose `items` list contains one `ItemResult` per package:
   - `skipped` if the package was already installed
   - `ok` if it was just installed successfully
   - `failed` if the install command failed for that package (detected by re-checking with `dpkg -s` after the install)
4. Top-level `status` is `failed` if any item failed, `skipped` if all were already installed, `ok` otherwise

Usage in a steps file:

```python
from framework.providers.apt import install_apt_packages

install_apt_packages("Shell Tools", [
    "ripgrep",
    "fd-find",
    "bat",
    "fzf",
    "curl",
    "git",
])
```

`install_apt_packages` is called at import time (not inside a function), causing the step to be registered immediately when the steps module is imported.

### Snap

```python
# framework/providers/snap.py

def install_snap_packages(group: str, packages: list[SnapPackage]) -> None: ...

@dataclass
class SnapPackage:
    name: str
    classic: bool = False
```

Registers a single step named `"snap packages"` under the given `group`. When run, it:

1. Checks each package using `snap list <n>` to determine which are already installed
2. Installs missing packages one at a time (snap does not support multi-package installs reliably), appending `--classic` where `classic=True`
3. Returns a `Result` whose `items` list contains one `ItemResult` per package:
   - `skipped` if already installed
   - `ok` if just installed successfully
   - `failed` if the install command exited non-zero
4. Top-level `status` is `failed` if any item failed, `skipped` if all were already installed, `ok` otherwise
4. Returns `ok("installed: pkg1, pkg2")` if all installs succeed, or `failed(...)` reporting which packages failed

Usage:

```python
from framework.providers.snap import install_snap_packages, SnapPackage

install_snap_packages("Developer Tools", [
    SnapPackage("nvim", classic=True),
    SnapPackage("slack", classic=True),
    SnapPackage("spotify"),
])
```

### Symlinks

```python
# framework/providers/symlinks.py

def symlink_dotfiles(group: str, dotfiles: list[Dotfile]) -> None: ...

@dataclass
class Dotfile:
    source: str  # relative path within the repo, e.g. "home/.zshrc"
    target: str  # path on the filesystem, e.g. "~/.zshrc" (~ is expanded)
```

Registers one step per `Dotfile` entry, each named after the target path (e.g. `"~/.zshrc"`), all under the given `group`. For each step, when run it:

1. Expands `~` in `target` using `os path.expanduser`
2. Resolves `source` relative to the repo root (the directory containing `main.py`), so paths are not sensitive to the working directory the script is launched from
3. If a symlink already exists at `target` pointing to the correct `source`, returns `skipped("already linked")`
4. If a symlink exists pointing elsewhere, removes it and creates the correct one, returning `ok("relinked")`
5. If a regular file or directory exists at `target`, returns `failed("target exists and is not a symlink")` — never overwrites real files
6. Otherwise creates the symlink and any necessary parent directories, returning `ok("linked")`

Usage:

```python
from framework.providers.symlinks import symlink_dotfiles, Dotfile

symlink_dotfiles("Dotfiles", [
    Dotfile("home/.zshrc",            "~/.zshrc"),
    Dotfile("home/.gitconfig",        "~/.gitconfig"),
    Dotfile("home/.config/nvim",      "~/.config/nvim"),
    Dotfile("home/.config/alacritty", "~/.config/alacritty"),
])
```

---

## Testing

- Use `pytest` (dev dependency only, not required to run the framework)
- Test `Result` constructors and fields
- Test `Runner`: registration order, exception handling, return values
- Test `Printer`: output format, TTY detection, ANSI stripping
- Test `shell.run`: mock `subprocess.run` to verify argument passing and result mapping
- Step functions in `steps/` can be tested by calling them directly and asserting on the returned `Result`; use `unittest.mock.patch` to mock `shutil.which`, `os.path`, and `shell.run`
- Test `apt.install_apt_packages`: verify it checks each package, produces correct `ItemResult` per package, top-level status rolls up correctly, and only missing packages are passed to the install command
- Test `snap.install_snap_packages`: verify `--classic` flag is applied correctly, each package gets its own `ItemResult`, partial failures produce a top-level `failed` status, and already-installed packages are `skipped`
- Test `Printer` sub-item rendering: verify indentation, icon selection, and column alignment for steps with `items`; verify emoji used for TTY, ASCII for non-TTY
- Test `symlinks.symlink_dotfiles`: verify correct-target skip, wrong-target relink, blocked-by-real-file failure, new symlink creation, and parent directory creation; mock `os.path`, `os.symlink`, `os.makedirs`, and `os.readlink`

---

## Non-goals

- No parallel execution
- No dependency ordering between steps
- No rollback
- No remote secrets or environment-specific config (keep that out of the repo)
- No support for non-Ubuntu systems (though little is Ubuntu-specific in the framework itself)