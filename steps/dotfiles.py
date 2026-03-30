from framework.providers.symlinks import symlink_dotfiles, Dotfile, REPO_ROOT

HOME_DIR = REPO_ROOT / "home"

dotfiles = [
    Dotfile(f"home/{p.relative_to(HOME_DIR)}", f"~/{p.relative_to(HOME_DIR)}")
    for p in HOME_DIR.rglob("*")
    if p.is_file()
]

symlink_dotfiles("Dotfiles", dotfiles)
