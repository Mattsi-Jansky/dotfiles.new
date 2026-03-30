# Dotfiles

## Overview

A lightweight Python framework for deterministic-ish machine configuration. It stores idempotent setup functions, executes them, and pretty-prints grouped results. No external dependencies. Clone the repo and run `python3 main.py`.

## Tests

```sh
pip install pytest
python3 -m pytest tests/
```

## Goals

- Runnable on a fresh Ubuntu machine with only `git` and `python3` (i.e. no external dependencies)
- Idempotent: safe to run repeatedly; steps should detect and skip already-complete work
- Steps are grouped and results are pretty-printed to the terminal with ANSI colours
- Failing steps must not abort the run; all steps should always be attempted
- The framework and the configuration that uses it live in separate layers
