import shutil

from framework import runner
from framework.result import Result, ok, skipped, failed
from framework.shell import run


@runner.step(group="Claude Code", name="Install Claude Code")
def install_claude_code() -> Result:
    if shutil.which("claude"):
        return skipped("already installed")
    result = run("curl -fsSL https://claude.ai/install.sh | bash")
    return ok() if result.success else failed(result.output)
