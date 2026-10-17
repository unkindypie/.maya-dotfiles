#!/usr/bin/env python3
"""Exercise installation and restoration in an empty home, plus config syntax."""
from pathlib import Path
import os, subprocess, tempfile, json
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='maya-dotfiles-test-') as d:
    env = dict(os.environ, HOME=d)
    def run(*args):
        subprocess.run(args, env=env, check=True, stdout=subprocess.DEVNULL)
    run('python3', str(root / 'install.py'), '--no-services')
    target = Path(d)
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
json.loads((root / 'home/.config/waybar/config').read_text())
for name in ['bootstrap-mvim.sh', 'home/.local/bin/maya-bar-action', 'home/.local/bin/maya-waybar', 'home/.local/bin/maya-git-status', 'home/scripts/tmux-sessionizer', 'home/scripts/tmux-sessionpicker']:
    subprocess.run(['bash', '-n', str(root / name)], check=True)
print('Fresh-home installation, symlink overwrite recovery, reinstall and syntax checks passed')
