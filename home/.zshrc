# Add bashrc settings
if [ -f ~/.bashrc ]; then
   source ~/.bashrc
fi

# Starship prompt
eval "$(starship init zsh)"

#Fortune prompt
fortune | randomsay | lolcat

# Include Autojump
[[ ! -f "/usr/share/autojump/autojump.sh" ]] || source /usr/share/autojump/autojump.sh

# cd shortcuts
setopt auto_cd  autocd
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'

# Autocompletion/Autosuggestion
autoload -U compinit
compinit
source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#BBB"

#Bat (cat replacement) theme`
export BAT_THEME="ansi-light"

#Ls colours
LS_COLORS='no=00;37:fi=00:di=00;33:ln=04;36:pi=40;33:so=01;35:bd=40;33;01:'
export LS_COLORS

#Fix oddly named Ubuntu binaries
alias yarn=yarnpkg
alias open=xdg-open

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
