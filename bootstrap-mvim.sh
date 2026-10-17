#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ ! -d "$HOME/maya-nvim/.git" ]]; then
  git clone https://github.com/unkindypie/maya-nvim.git "$HOME/maya-nvim"
  revision=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["mvim"]["commit"])' "$root/dependencies.json")
  git -C "$HOME/maya-nvim" checkout "$revision"
fi
# Upstream installer installs Neovim, plugins and the mvim launcher.
"$HOME/maya-nvim/install.sh" "$@"
python3 "$root/install.py"
