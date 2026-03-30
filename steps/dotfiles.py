from framework.providers.symlinks import symlink_dotfiles, Dotfile

symlink_dotfiles("Dotfiles", [
    Dotfile("home/.zshrc",      "~/.zshrc"),
    Dotfile("home/.gitconfig",  "~/.gitconfig"),
    Dotfile("home/.aliases",    "~/.aliases"),
    Dotfile("home/.funcs",      "~/.funcs"),
    Dotfile("home/.npmrc",      "~/.npmrc"),
])
