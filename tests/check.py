#!/usr/bin/env python3
"""Exercise installation and restoration in an empty home, plus config syntax."""
from pathlib import Path
import os, subprocess, tempfile, json, shutil
source_root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='maya-dotfiles-test-') as d:
    root = Path(d) / 'checkout'
    shutil.copytree(source_root, root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    target = Path(d) / 'user'
    target.mkdir()
    env = dict(os.environ, HOME=str(target))
    def run(*args):
        if len(args) > 1 and args[1] == str(root / 'install.py'):
            args = (*args, '--skip-dependencies')
        subprocess.run(args, env=env, check=True, stdout=subprocess.DEVNULL)
    (target / '.zshrc').write_text('export EXAMPLE_API_TOKEN="test-only-credential"\n')
    run('python3', str(root / 'install.py'), '--no-services', '--without-mvim')
    secret = target / '.config/zsh/secrets.zsh'
    assert 'test-only-credential' in secret.read_text()
    assert secret.stat().st_mode & 0o777 == 0o600
    assert 'test-only-credential' not in (target / '.zshrc').read_text()
    for name in ['.config/kitty/kitty.conf', '.config/waybar/config', '.config/mvim/init.lua', '.tmux.conf']:
        assert (target / name).is_symlink()
        assert (target / name).resolve() == root / 'home' / name
        assert (target / name).read_bytes() == (root / 'home' / name).read_bytes()
    for src in (root / 'color-palette').iterdir():
        installed = target / '.config/maya-theme' / src.name
        assert installed.is_symlink()
        assert installed.resolve() == src
    palette_link = target / '.config/maya-theme/palette.json'
    palette_link.unlink()
    palette_link.write_text('{}')
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert palette_link.resolve() == root / 'color-palette/palette.json'
    # Simulate KooL replacing a managed entry point with a symlink.
    config = target / '.config/waybar/config'
    config.unlink()
    vendor = target / 'vendor-config'; vendor.write_text('{}')
    config.symlink_to(vendor)
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert config.is_symlink()
    assert config.resolve() == root / "home/.config/waybar/config"
    assert config.read_bytes() == (root / 'home/.config/waybar/config').read_bytes()
    assert vendor.read_text() == '{}'
    # Editing an installed config must change the checkout, not get copied back.
    style = target / '.config/waybar/style.css'
    style.write_text(style.read_text() + '\n/* live edit */\n')
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert '/* live edit */' in (root / 'home/.config/waybar/style.css').read_text()
    # Whole-directory replacements are also repaired without writing vendor files.
    bar = target / '.config/waybar'
    bar.rename(target / 'old-waybar')
    bar.mkdir()
    (bar / 'config').write_text('{}')
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert (bar / 'config').resolve() == root / 'home/.config/waybar/config'
    assert not (target / '.zshrc').is_symlink()
    assert (target / '.config/zsh/shared.zsh').is_symlink()
    run('python3', str(root / 'install.py'), '--no-services')
    # Reuse a fake existing checkout: optional path must invoke it once, then
    # restore the personal override without recursive dotfiles installation.
    editor = target / 'maya-nvim'
    (editor / '.git').mkdir(parents=True)
    installer = editor / 'install.sh'
    installer.write_text('#!/bin/sh\nprintf called >> "$HOME/editor-called"\nprintf upstream > "$HOME/.config/mvim/replacement"; mv "$HOME/.config/mvim/replacement" "$HOME/.config/mvim/init.lua"\n')
    installer.chmod(0o755)
    run('python3', str(root / 'install.py'), '--no-services', '--with-mvim')
    assert (target / 'editor-called').read_text() == 'called'
    assert (target / '.config/mvim/init.lua').read_bytes() == (root / 'home/.config/mvim/init.lua').read_bytes()
root = source_root
json.loads((root / 'home/.config/waybar/config').read_text())
for name in ['bootstrap-mvim.sh', 'home/.local/bin/maya-bar-action', 'home/.local/bin/maya-waybar', 'home/.local/bin/maya-git-status', 'home/scripts/tmux-sessionizer', 'home/scripts/tmux-sessionpicker']:
    subprocess.run(['bash', '-n', str(root / name)], check=True)
subprocess.run(['zsh', '-n', str(root / 'home/.config/zsh/shared.zsh')], check=True)
print('Fresh-home install, credential preservation, optional editor, recovery and syntax checks passed')
