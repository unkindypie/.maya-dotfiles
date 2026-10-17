#!/usr/bin/env python3
"""Install missing pinned dependencies, preserving all existing installations."""
from pathlib import Path
import json, os, re, subprocess, tempfile


def install_one(spec, target):
    target = Path(target)
    if target.exists() or target.is_symlink():
        print(f'Keeping existing dependency: {target}')
        return
    revision = spec['commit']
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError(f'Invalid pinned revision for {target.name}')
    target.parent.mkdir(parents=True, exist_ok=True)
    # Fetch in a sibling directory: failures never leave half-installed targets.
    with tempfile.TemporaryDirectory(prefix='.maya-dependency-', dir=target.parent) as tmp:
        checkout = Path(tmp) / 'checkout'
        subprocess.run(['git', 'init', '--quiet', str(checkout)], check=True)
        subprocess.run(['git', '-C', str(checkout), 'fetch', '--quiet', '--depth=1', spec['url'], revision], check=True)
        subprocess.run(['git', '-C', str(checkout), 'checkout', '--quiet', '--detach', 'FETCH_HEAD'], check=True)
        actual = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != revision:
            raise RuntimeError(f'Revision verification failed for {target.name}')
        subprocess.run(['git', '-C', str(checkout), 'remote', 'add', 'origin', spec['url']], check=True)
        os.rename(checkout, target)
    print(f'Installed {target.name} at {revision[:12]}')


def install_all(root, home):
    data = json.loads((root / 'dependencies.json').read_text())
    install_one(data['oh_my_zsh'], home / '.oh-my-zsh')
    if not (home / '.oh-my-zsh/oh-my-zsh.sh').is_file():
        raise SystemExit('Existing ~/.oh-my-zsh is incomplete; move it aside and rerun to install the framework.')
    for name in ['zsh-autosuggestions', 'zsh-syntax-highlighting']:
        install_one(data[name], home / '.oh-my-zsh/custom/plugins' / name)
    for name, spec in data['tmux_plugins'].items():
        install_one(spec, home / '.tmux/plugins' / name)


if __name__ == '__main__':
    install_all(Path(__file__).resolve().parents[1], Path.home())
