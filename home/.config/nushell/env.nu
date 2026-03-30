# PATH
$env.PATH = ($env.PATH | split row (char esep) | prepend $"($env.HOME)/.cargo/bin")

# Environment variables
$env.BAT_THEME = "ansi-light"
$env.EDITOR = "nvim"

# fnm (Node version manager)
if (fnm list | complete | get exit_code) == 0 {
    fnm env --json | from json | load-env
    $env.PATH = ($env.PATH | prepend $"($env.FNM_MULTISHELL_PATH)/bin")
}
$env.FNM_VERSION_FILE_STRATEGY = "recursive"

# Starship prompt
mkdir ~/.cache/starship
starship init nu | save -f ~/.cache/starship/init.nu

# Zoxide
mkdir ~/.cache/zoxide
zoxide init nushell | save -f ~/.cache/zoxide/init.nu
