# PATH
$env.PATH = ($env.PATH | split row (char esep) | prepend $"($env.HOME)/.cargo/bin")

# Environment variables
$env.BAT_THEME = "ansi-light"
$env.EDITOR = "nvim"

# fnm (Node version manager)
fnm env --json | from json | load-env
$env.FNM_VERSION_FILE_STRATEGY = "recursive"

# Starship prompt
mkdir ~/.cache/starship
starship init nu | save -f ~/.cache/starship/init.nu

# Zoxide
mkdir ~/.cache/zoxide
zoxide init nushell | save -f ~/.cache/zoxide/init.nu
