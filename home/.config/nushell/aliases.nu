# Zoxide
alias j = z

# Git
alias gs = git status -sb
alias gb = git branch
alias gc = git commit --verbose
alias gca = git commit --verbose --all
alias gcf = git commit --fixup HEAD
alias gco = git checkout
alias gia = git add
alias gm = git merge
alias gpush = git push
alias gpull = git pull
alias gpf = git push --force-with-lease
alias gr = git rebase
alias gra = git rebase --abort
alias grc = git rebase --continue
alias gri = git rebase --interactive
alias gst = git stash
alias gwd = git diff --no-ext-diff
alias gu = git reset HEAD~1
alias gspop = git stash pop
alias gtree = git log --all --graph --decorate --oneline
alias gph = git push -u origin HEAD

# Cargo
alias c = cargo
alias cw = cargo watch --clear -x

# Docker
alias dr = docker
alias dc = docker compose

# Utilities
alias vim = nvim
alias yarn = yarnpkg
alias l = ls
alias cat = batcat
