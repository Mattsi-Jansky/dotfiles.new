# Do nothing in non-interactive shells. GDM's Xsession is a bash script that
# sources ~/.profile (and so this file); any stderr output here pops a blocking
# error dialog that stops the desktop session from starting.
[[ $- == *i* ]] || return

source ~/.aliases
source ~/.funcs

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

#Cargo binaries
export PATH=$PATH:$HOME/.cargo/bin

# mise activation
command -v mise >/dev/null && eval "$(mise activate bash)"

#Local RC for settings relevant to the local machine I don't want to push to my dotfiles
if [[ -f "$HOME/.localrc" ]]; then
  source "$HOME/.localrc"
fi
