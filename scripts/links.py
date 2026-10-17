"""Shared, non-destructive file-link installation and repair."""
from pathlib import Path
from datetime import datetime
import os, shutil, tempfile


def backup_root(home):
    return home / '.local/state/maya-dotfiles/backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')


def save_existing(dst, home, backup):
    saved = backup / dst.relative_to(home)
    saved.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_dir() and not dst.is_symlink():
        shutil.move(str(dst), str(saved))
    elif dst.is_symlink():
        saved.symlink_to(os.readlink(dst))
    else:
        shutil.copy2(dst, saved)
        if dst.name == '.zshrc':
            saved.chmod(0o600)


def ensure_link(src, dst, home, backup):
    if dst.is_symlink() and dst.resolve() == src.resolve():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        save_existing(dst, home, backup)
    # Atomic replacement prevents readers seeing a partially installed file.
    with tempfile.TemporaryDirectory(prefix='.maya-link-', dir=dst.parent) as tmp:
        link = Path(tmp) / 'link'
        link.symlink_to(src.resolve())
        os.replace(link, dst)
    return True
