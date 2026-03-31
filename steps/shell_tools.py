from framework import runner
from framework.result import Result
from framework.providers.apt import install_apt_packages
from framework.providers.cargo import cargo_install

install_apt_packages("Shell Tools", [
    "autojump",
    "bat",
    "cmake",
    "cowsay",
    "curl",
    "fd-find",
    "fish",
    "fortune-mod",
    "fzf",
    "git",
    "git-lfs",
    "graphviz",
    "jq",
    "libxcb-xfixes0-dev",
    "lolcat",
    "neovim",
    "pkg-config",
    "ripgrep",
    "snapd",
    "xclip",
    "xsel",
    "yarnpkg",
    "zsh",
])


@runner.step(group="Shell Tools", name="git-delta")
def install_git_delta() -> Result:
    return cargo_install("git-delta")
