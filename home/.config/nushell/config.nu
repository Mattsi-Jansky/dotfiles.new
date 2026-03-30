# Starship prompt
use ~/.cache/starship/init.nu

# Custom functions
source ~/.config/nushell/funcs.nu

# Fortune prompt
fortune | randomsay | lolcat

# fnm auto-switch on cd (reads .nvmrc)
$env.config.hooks.env_change.PWD = (
    $env.config.hooks.env_change.PWD | append {|| fnm use --silent-if-unchanged}
)

# Zoxide (autojump replacement)
source ~/.cache/zoxide/init.nu

# Aliases
source ~/.config/nushell/aliases.nu
