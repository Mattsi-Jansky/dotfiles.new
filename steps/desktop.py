import os
import shlex

from framework import runner
from framework.result import ItemResult, skipped
from framework.shell import run

# (label, command) pairs, one list per desktop environment. The lists mirror
# each other where the desktop has an equivalent setting.

GNOME_SETTINGS = [
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
GNOME_COMMANDS = [(label, f"gsettings set {setting}") for label, setting in GNOME_SETTINGS]


def _kwrite(file: str, groups: list[str], key: str, value: str) -> str:
    group_args = " ".join(f"--group {shlex.quote(g)}" for g in groups)
    type_arg = "--type bool " if value in ("true", "false") else ""
    return f"kwriteconfig6 --notify --file {file} {group_args} --key {key} {type_arg}{shlex.quote(value)}"


def _dbus(dest: str, path: str, method: str, *args: str) -> str:
    quoted_args = " ".join(shlex.quote(a) for a in args)
    return f"dbus-send --session --print-reply --dest={dest} {path} {method} {quoted_args}".rstrip()


# Qt key codes, as kglobalaccel expects them over DBus
QT_META = 0x10000000
QT_F1 = 0x01000030


def _set_shortcut(component: str, action: str, *keys: int) -> str:
    action_id = f"['{component}', '{action}', '', '']"
    key_list = "[" + ", ".join(f"([{k}, 0, 0, 0],)" for k in keys) + "]"
    return (f"gdbus call --session --dest org.kde.kglobalaccel --object-path /kglobalaccel "
            f"--method org.kde.KGlobalAccel.setForeignShortcutKeys \"{action_id}\" '{key_list}'")


PANEL_SCRIPT = 'panels().forEach(function (p) { p.location = "bottom"; p.hiding = "autohide"; });'
POWER_PROFILES = ["AC", "Battery", "LowBattery"]

# Plasma 6. Not listed because they are already the Plasma defaults: virtual
# desktops span all screens, and the home folder is not shown on the desktop.
KDE_COMMANDS = [
    # The global theme also switches GTK apps to Breeze Dark
    ("Dark mode", "plasma-apply-lookandfeel -a org.kde.breezedark.desktop"),
    ("Panel at bottom, auto-hide", _dbus(
        "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript",
        f"string:{PANEL_SCRIPT}")),
    ("Night light", _kwrite("kwinrc", ["NightColor"], "Active", "true")),
    ("Night light temperature", _kwrite("kwinrc", ["NightColor"], "NightTemperature", "3500")),
    ("App switcher only shows current workspace", _kwrite("kwinrc", ["TabBox"], "DesktopMode", "1")),
    ("App switcher only shows current screen", _kwrite("kwinrc", ["TabBox"], "MultiScreenMode", "1")),
    *[(f"Performance power profile ({p})", _kwrite("powerdevilrc", [p, "Performance"], "PowerProfile", "performance"))
      for p in POWER_PROFILES[:2]],
    *[(f"No dimming screen on inactivity ({p})", _kwrite("powerdevilrc", [p, "Display"], "DimDisplayWhenIdle", "false"))
      for p in POWER_PROFILES],
    *[(f"Do not switch screen off after inactivity ({p})", _kwrite("powerdevilrc", [p, "Display"], "TurnOffDisplayWhenIdle", "false"))
      for p in POWER_PROFILES],
    # Default is Meta+Fn and Ctrl+Fn; drop Ctrl+Fn so it reaches apps (e.g. Ctrl+F4 closes Firefox tabs)
    *[(f"Switch to desktop {n} with Meta+F{n} only", _set_shortcut("kwin", f"Switch to Desktop {n}", QT_META | (QT_F1 + n - 1)))
      for n in range(1, 5)],
    ("Reload KWin", _dbus("org.kde.KWin", "/KWin", "org.kde.KWin.reconfigure")),
    ("Reload power management", _dbus(
        "org.kde.Solid.PowerManagement", "/org/kde/Solid/PowerManagement",
        "org.kde.Solid.PowerManagement.reparseConfiguration")),
]

DESKTOPS = {
    "GNOME": GNOME_COMMANDS,
    "KDE": KDE_COMMANDS,
}


def _current_desktop() -> str | None:
    # XDG_CURRENT_DESKTOP is a colon-separated list, e.g. "ubuntu:GNOME"
    names = os.environ.get("XDG_CURRENT_DESKTOP", "").upper().split(":")
    return next((name for name in DESKTOPS if name in names), None)


def _apply(commands: list[tuple[str, str]]):
    for label, command in commands:
        result = run(command)
        if result.success:
            yield ItemResult(name=label, status="ok")
        else:
            yield ItemResult(name=label, status="failed", message=result.output)


@runner.step(group="Desktop", name="Desktop settings", skip_in_test=True)
def apply_desktop_settings():
    desktop = _current_desktop()
    if desktop is None:
        current = os.environ.get("XDG_CURRENT_DESKTOP") or "none"
        return skipped(f"unsupported desktop: {current}")
    return _apply(DESKTOPS[desktop])
