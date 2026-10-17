#!/usr/bin/env python3
"""Install into the current user's home; back up replaced files first."""
from pathlib import Path
from datetime import datetime
import argparse, shutil, subprocess
p = argparse.ArgumentParser()
p.add_argument('--no-services', action='store_true', help='Copy files only (for tests/non-systemd hosts)')
a = p.parse_args()
root = Path(__file__).resolve().parent
home = Path.home()
backup = home / '.local/state/maya-dotfiles/backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
for src in (root / 'home').rglob('*'):
    if not src.is_file(): continue
    rel = src.relative_to(root / 'home'); dst = home / rel
    if dst.is_file() and not dst.is_symlink() and dst.read_bytes() == src.read_bytes(): continue
    if dst.exists() or dst.is_symlink():
        saved = backup / rel; saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, saved, follow_symlinks=True)
        if dst.is_symlink(): dst.unlink()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
if shutil.which('fc-cache'): subprocess.run(['fc-cache', '-f'], check=True)
if not a.no_services:
    units = home / '.config/systemd/user'; units.mkdir(parents=True, exist_ok=True)
    restore = units / 'maya-dotfiles-restore.service'
    restore.write_text('[Unit]\nDescription=Restore Maya paper appearance after vendor updates\n[Service]\nType=oneshot\nExecStart=/usr/bin/python3 "' + str(root / 'scripts/restore-managed.py') + '"\n')
    (units / 'maya-dotfiles.path').write_text("""[Unit]
Description=Protect Maya Waybar and Kitty configuration
[Path]
PathChanged=%h/.config
PathChanged=%h/.config/waybar
PathChanged=%h/.config/waybar/config
PathChanged=%h/.config/waybar/style.css
PathChanged=%h/.config/kitty
PathChanged=%h/.config/kitty/kitty.conf
PathChanged=%h/.local/share/kitty-personal
Unit=maya-dotfiles-restore.service
[Install]
WantedBy=default.target
""")
    restore_script = root / 'scripts/restore-managed.py'
    (units / 'maya-waybar.service').write_text(f"""[Unit]
Description=Maya Paper Waybar
After=graphical-session-pre.target
[Service]
ExecStartPre=/usr/bin/python3 "{restore_script}"
ExecStart=%h/.local/bin/maya-waybar
Restart=always
RestartSec=3
[Install]
WantedBy=default.target
""")
    def ctl(*args, check=True): subprocess.run(['systemctl', '--user', *args], check=check)
    ctl('disable', '--now', 'kitty-notebook.path', check=False)
    ctl('disable', '--now', 'waybar.service', check=False)
    ctl('daemon-reload')
    ctl('import-environment', 'WAYLAND_DISPLAY', 'XDG_CURRENT_DESKTOP', check=False)
    subprocess.run(['pkill', '-x', 'waybar'], check=False)
    ctl('enable', '--now', 'maya-dotfiles.path', 'maya-waybar.service')
    ctl('restart', 'maya-waybar.service')
print('Installed. Backups:', backup)
