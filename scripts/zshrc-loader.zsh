# Local entry point: keep secrets out of the shared dotfiles repository.
[[ -f "$HOME/.config/zsh/local.zsh" ]] && source "$HOME/.config/zsh/local.zsh"
[[ -f "$HOME/.config/zsh/secrets.zsh" ]] && source "$HOME/.config/zsh/secrets.zsh"
source "$HOME/.config/zsh/shared.zsh"
