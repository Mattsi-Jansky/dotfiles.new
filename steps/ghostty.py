from framework.providers.snap import install_snap_packages, SnapPackage
from framework.providers.symlinks import symlink_dotfiles, Dotfile

install_snap_packages("Ghostty", [
    SnapPackage("ghostty", classic=True),
], skip_in_test=True)

symlink_dotfiles("Ghostty", [
    Dotfile("config/ghostty/config.ghostty", "~/.config/ghostty/config.ghostty"),
])
