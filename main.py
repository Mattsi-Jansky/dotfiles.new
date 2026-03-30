# Steps run in import order. Ordering matters!
import steps.shell_tools
import steps.snap_tools
import steps.rust                 # installs cargo
import steps.fnm                  # needs cargo
import steps.nushell              # needs cargo
import steps.starship
import steps.claude_code
import steps.dotfiles

from framework import runner
from framework.printer import print_results, print_summary
import sys

if __name__ == "__main__":
    outcomes = print_results(runner.run_all())
    print_summary(outcomes)
    sys.exit(0 if all(o.result.status != "failed" for o in outcomes) else 1)
