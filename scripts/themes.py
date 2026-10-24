"""Install stable theme aliases; the current link is the only persistent mode state."""
from pathlib import Path
import os
from links import ensure_alias

ALIASES = {
    '.config/maya-theme/palette.json': 'palette.json',
    '.config/maya-theme/colors.conf': 'colors.conf',
    '.config/maya-theme/colors.lua': 'colors.lua',
    '.config/maya-theme/kitty.conf': 'kitty.conf',
    '.config/waybar/palette.css': 'palette.css',
    '.config/swaync/palette.css': 'palette.css',
    '.config/rofi/themes/maya-palette.rasi': 'rofi.rasi',
    '.config/wofi/style.css': 'wofi.css',
    '.config/btop/themes/maya-paper.theme': 'btop.theme',
}


def mode(home):
    current = home / '.config/maya-theme/current'
    if current.is_symlink():
        selected = Path(os.readlink(current)).name
        if selected in ('light', 'dark'):
            return selected
    return 'light'


def install_profiles(root, home, backup):
    base = home / '.config/maya-theme'
    selected = mode(home)
    changed = ensure_alias(root / 'color-palette/profiles', base / 'profiles', home, backup)
    changed |= ensure_alias(base / 'profiles' / selected, base / 'current', home, backup)
    for name, filename in ALIASES.items():
        changed |= ensure_alias(base / 'current' / filename, home / name, home, backup)
    return changed
