#!/usr/bin/env python3
"""Install into the current user's home; back up replaced files first."""
from pathlib import Path
from datetime import datetime
import argparse, shutil, subprocess, sys, re, os, runpy
p = argparse.ArgumentParser()
p.add_argument('--skip-dependencies', action='store_true', help='Skip dependency downloads (offline config-only install)')
p.add_argument('--no-services', action='store_true', help='Copy files only (for tests/non-systemd hosts)')
mvim = p.add_mutually_exclusive_group()
mvim.add_argument('--with-mvim', dest='with_mvim', action='store_true', help='Install Maya Neovim and its launcher')
mvim.add_argument('--without-mvim', dest='with_mvim', action='store_false', help='Skip the optional Maya Neovim installation')
p.set_defaults(with_mvim=None)
a = p.parse_args()
root = Path(__file__).resolve().parent
home = Path.home()
if not a.skip_dependencies:
    # Do this before copying custom themes, which also live under .oh-my-zsh.
    deps = runpy.run_path(str(root / 'scripts/install-dependencies.py'))
    deps['install_all'](root, home)
if a.with_mvim is None:
    a.with_mvim = (sys.stdin.isatty() and
                   input('Install Maya Neovim (maya-nvim) too? [y/N] ').strip().lower() in ('y', 'yes'))
if a.with_mvim:
    # Run before copying overrides so the saved personal config wins afterward.
    subprocess.run(['bash', str(root / 'bootstrap-mvim.sh'), '--from-installer'], check=True)
backup = home / '.local/state/maya-dotfiles/backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
# Preserve single-line credential assignments before replacing a pre-existing zshrc.
# Never print their values or copy them into the repository.
zshrc = home / '.zshrc'
if zshrc.is_file():
    private = []
    for line in zshrc.read_text().splitlines():
        match = re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=', line)
        if match and re.search(r'(?i)(token|secret|password|passwd|api_?key|account_sid|credential)', match[1]):
            if line.rstrip().endswith('\\'):
                raise SystemExit('Move multiline credentials to ~/.config/zsh/secrets.zsh before installing.')
            private.append(line)
    if private:
        secrets = home / '.config/zsh/secrets.zsh'
        secrets.parent.mkdir(parents=True, exist_ok=True)
        current = secrets.read_text() if secrets.exists() else '# Machine-local credentials; never commit this file.\n'
        additions = [line for line in private if line not in current.splitlines()]
        fd = os.open(secrets, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(current.rstrip() + '\n' + ('\n'.join(additions) + '\n' if additions else ''))
        secrets.chmod(0o600)
for src in (root / 'home').rglob('*'):
    if not src.is_file(): continue
    rel = src.relative_to(root / 'home'); dst = home / rel
    if dst.is_file() and not dst.is_symlink() and dst.read_bytes() == src.read_bytes(): continue
    if dst.exists() or dst.is_symlink():
        saved = backup / rel; saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, saved, follow_symlinks=True)
        if rel == Path('.zshrc'): saved.chmod(0o600)
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
