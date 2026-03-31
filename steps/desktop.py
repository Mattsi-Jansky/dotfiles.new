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
    ("Workspaces in all screens", "org.gnome.mutter workspaces-only-on-primary false"),
    ("App switcher only shows current workspace", "org.gnome.shell.extensions.tiling-assistant tiling-popup-all-workspace false"),
    ("App switcher only shows current screen", "org.gnome.shell.extensions.dash-to-dock isolate-monitors true"),
    ("Performance battery mode", "org.gnome.shell last-selected-power-profile 'performance'"),
    ("No dimming screen on inactivity", "org.gnome.settings-daemon.plugins.power idle-dim false"),
    ("Do not switch screen off after inactivity", "org.gnome.desktop.session idle-delay 0"),
    ("Hide home folder on desktop", "org.gnome.shell.extensions.ding show-home false")
]


@runner.step(group="Desktop", name="GNOME settings", skip_in_test=True)
def apply_desktop_settings():
    for label, setting in SETTINGS:
        result = run(f"gsettings set {setting}")
        if result.success:
            yield ItemResult(name=label, status="ok")
        else:
            yield ItemResult(name=label, status="failed", message=result.output)
