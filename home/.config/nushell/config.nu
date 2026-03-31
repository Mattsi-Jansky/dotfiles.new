$env.config.show_banner = false

# Starship prompt
use ~/.cache/starship/init.nu

# Custom functions
source ~/.config/nushell/funcs.nu

# Fortune prompt
fortune | randomsay | lolcat

# fnm auto-switch on cd (reads .nvmrc)
$env.config = ($env.config
    | upsert hooks { default {} }
    | upsert hooks.env_change { default {} }
    | upsert hooks.env_change.PWD { default [] }
)
$env.config.hooks.env_change.PWD = (
    $env.config.hooks.env_change.PWD | append {||
        if (fnm default | complete | get exit_code) == 0 {
            fnm use --silent-if-unchanged --install-if-missing
        }
    }
)

# Zoxide (autojump replacement)
source ~/.cache/zoxide/init.nu

# Aliases
source ~/.config/nushell/aliases.nu
