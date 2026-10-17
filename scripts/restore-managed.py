#!/usr/bin/env python3
"""Restore the paper bar and Kitty entry points without modifying vendor scripts."""
from pathlib import Path
import shutil, subprocess
root = Path(__file__).resolve().parents[1]
home = Path.home()
waybar_changed = False
managed = ['.config/waybar/config', '.config/waybar/style.css', '.config/kitty/kitty.conf']
for name in managed:
    src, dst = root / 'home' / name, home / name
    if dst.is_symlink() or not dst.is_file() or dst.read_bytes() != src.read_bytes():
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.is_symlink():
            dst.unlink()
        shutil.copy2(src, dst)
        waybar_changed |= name.startswith('.config/waybar/')
# Restore assets/includes too if an updater deletes them.
for folder in ['.local/share/kitty-personal', '.config/kitty/kitty-themes']:
    for src in (root / 'home' / folder).rglob('*'):
        if src.is_file():
            dst = home / src.relative_to(root / 'home')
            if not dst.is_file() or dst.read_bytes() != src.read_bytes():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

if waybar_changed:
    # A vendor may have launched Waybar before restoration finished.
    subprocess.run(['systemctl', '--user', '--no-block', 'try-restart',
                    'maya-waybar.service'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=False)
