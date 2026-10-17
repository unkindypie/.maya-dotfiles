#!/usr/bin/env python3
"""Exercise installation and restoration in an empty home, plus config syntax."""
from pathlib import Path
import os, subprocess, tempfile, json
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='maya-dotfiles-test-') as d:
    env = dict(os.environ, HOME=d)
    def run(*args):
        subprocess.run(args, env=env, check=True, stdout=subprocess.DEVNULL)
    target = Path(d)
    (target / '.zshrc').write_text('export EXAMPLE_API_TOKEN="test-only-credential"\n')
    run('python3', str(root / 'install.py'), '--no-services', '--without-mvim')
    secret = target / '.config/zsh/secrets.zsh'
    assert 'test-only-credential' in secret.read_text()
    assert secret.stat().st_mode & 0o777 == 0o600
    assert 'test-only-credential' not in (target / '.zshrc').read_text()
    for name in ['.config/kitty/kitty.conf', '.config/waybar/config', '.config/mvim/init.lua', '.tmux.conf']:
        assert (target / name).read_bytes() == (root / 'home' / name).read_bytes()
    # Simulate KooL replacing a managed entry point with a symlink.
    config = target / '.config/waybar/config'
    config.unlink()
    vendor = target / 'vendor-config'; vendor.write_text('{}')
    config.symlink_to(vendor)
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert not config.is_symlink()
    assert config.read_bytes() == (root / 'home/.config/waybar/config').read_bytes()
    assert vendor.read_text() == '{}'
    run('python3', str(root / 'install.py'), '--no-services')
    # Reuse a fake existing checkout: optional path must invoke it once, then
    # restore the personal override without recursive dotfiles installation.
    editor = target / 'maya-nvim'
    (editor / '.git').mkdir(parents=True)
    installer = editor / 'install.sh'
    installer.write_text('#!/bin/sh\nprintf called >> "$HOME/editor-called"\nprintf upstream > "$HOME/.config/mvim/init.lua"\n')
    installer.chmod(0o755)
    run('python3', str(root / 'install.py'), '--no-services', '--with-mvim')
    assert (target / 'editor-called').read_text() == 'called'
    assert (target / '.config/mvim/init.lua').read_bytes() == (root / 'home/.config/mvim/init.lua').read_bytes()
json.loads((root / 'home/.config/waybar/config').read_text())
for name in ['bootstrap-mvim.sh', 'home/.local/bin/maya-bar-action', 'home/.local/bin/maya-waybar', 'home/.local/bin/maya-git-status', 'home/scripts/tmux-sessionizer', 'home/scripts/tmux-sessionpicker']:
    subprocess.run(['bash', '-n', str(root / name)], check=True)
subprocess.run(['zsh', '-n', str(root / 'home/.zshrc')], check=True)
print('Fresh-home install, credential preservation, optional editor, recovery and syntax checks passed')
