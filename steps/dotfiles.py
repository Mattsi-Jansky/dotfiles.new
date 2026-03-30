from framework.providers.symlinks import symlink_dotfiles, Dotfile

symlink_dotfiles("Dotfiles", [
    Dotfile("home/.zshrc",            "~/.zshrc"),
    Dotfile("home/.gitconfig",        "~/.gitconfig"),
])
