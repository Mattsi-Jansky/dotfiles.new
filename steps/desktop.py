from framework import runner
from framework.result import Result, ItemResult
from framework.shell import run

SETTINGS = [
    ("Dark mode", "org.gnome.desktop.interface color-scheme 'prefer-dark'"),
    ("Dark GTK theme", "org.gnome.desktop.interface gtk-theme 'Yaru-dark'"),
    ("Dock position", "org.gnome.shell.extensions.dash-to-dock dock-position 'BOTTOM'"),
    ("Dock auto-hide", "org.gnome.shell.extensions.dash-to-dock dock-fixed false"),
    ("Dock icon size", "org.gnome.shell.extensions.dash-to-dock dash-max-icon-size 36"),
    ("Night light", "org.gnome.settings-daemon.plugins.color night-light-enabled true"),
    ("Night light temperature", "org.gnome.settings-daemon.plugins.color night-light-temperature 3500"),
    ("Show hidden files", "org.gnome.nautilus.preferences show-hidden-files true"),
    ("Sort folders first", "org.gnome.nautilus.preferences sort-directories-first true"),
    ("List view in files", "org.gnome.nautilus.preferences default-folder-viewer 'list-view'"),
]


@runner.step(group="Desktop", name="GNOME settings", skip_in_test=True)
def apply_desktop_settings():
    for label, setting in SETTINGS:
        result = run(f"gsettings set {setting}")
        if result.success:
            yield ItemResult(name=label, status="ok")
        else:
            yield ItemResult(name=label, status="failed", message=result.output)
