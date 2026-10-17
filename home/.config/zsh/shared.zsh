# Portable personal shell configuration. Secrets belong in ~/.config/zsh/secrets.zsh.
export ZSH="$HOME/.oh-my-zsh"
# ZSH_THEME="agnosterzak"
ZSH_THEME="tonotdo"
# ZSH_THEME="sobole"
# export SOBOLE_THEME_MODE="light"

plugins=(git)
(( $+commands[dnf] )) && plugins+=(dnf)
plugins+=(zsh-autosuggestions zsh-syntax-highlighting)
[[ -f "$ZSH/oh-my-zsh.sh" ]] && source "$ZSH/oh-my-zsh.sh"

if [[ -n "$TMUX" ]] && (( $+commands[fastfetch] )); then
  if (( $+commands[pokemon-colorscripts] )) && [[ -f "$HOME/.config/fastfetch/config-pokemon.jsonc" ]]; then
    pokemon-colorscripts --no-title -r 1-3 | fastfetch -c "$HOME/.config/fastfetch/config-pokemon.jsonc" --logo-type file-raw --logo-height 10 --logo-width 5 --logo -
  else
    fastfetch
  fi
fi
(( $+commands[fzf] )) && source <(fzf --zsh)
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt appendhistory
if (( $+commands[lsd] )); then
  alias ls='lsd'
  alias lt='ls --tree'
fi
alias l='ls -l'
alias la='ls -a'
alias lla='ls -la'
[[ -x "$HOME/.local/bin/lvim" ]] && alias lvim="$HOME/.local/bin/lvim"
alias docker-compose='docker compose'
[[ -s "$HOME/.bun/_bun" ]] && source "$HOME/.bun/_bun"
export BUN_INSTALL="$HOME/.bun"
typeset -U path
path=("$HOME/.local/bin" "$HOME/scripts" "$HOME/.cargo/bin" "$BUN_INSTALL/bin" $path)
export PYENV_ROOT="$HOME/.pyenv"
[[ -d "$PYENV_ROOT/bin" ]] && path=("$PYENV_ROOT/bin" $path)
(( $+commands[pyenv] )) && eval "$(pyenv init -)"
alias ps='eval "$(poetry env activate)" && clear'
[[ -x "$HOME/.local/bin/mvim" ]] && alias mvim="$HOME/.local/bin/mvim"
if (( $+commands[tmux] )) && [[ -o interactive && -z "$TMUX" && "$TERM" != screen* && "$TERM" != tmux* ]]; then
  exec tmux
fi
