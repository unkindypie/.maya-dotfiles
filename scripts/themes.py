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
    for variant in ('light', 'dark'):
        name = 'Maya-Paper-' + variant.title()
        profile = base / 'profiles' / variant
        changed |= ensure_alias(profile / 'gtk-theme', home / '.local/share/themes' / name, home, backup)
        icons = home / '.local/share/icons' / name
        changed |= ensure_alias(profile / 'icons/scalable', icons / 'scalable', home, backup)
        # A usable fallback even before toolkit preferences are applied.
        if not (icons / 'index.theme').exists():
            write_icon_index(home, name, 'Adwaita', backup)
            changed = True
    for version in ('qt5ct', 'qt6ct'):
        changed |= ensure_alias(base / 'current' / ('qt' + version[2] + '.conf'),
                                home / '.config' / version / 'colors/Maya-Paper.conf', home, backup)
    return changed


def write_icon_index(home, name, fallback, backup):
    from links import save_existing
    path = home / '.local/share/icons' / name / 'index.theme'
    content = (f'[Icon Theme]\nName={name}\nComment=Maya pastel folder overlay\n'
               f'Inherits={fallback}\nDirectories=scalable/places\n\n'
               '[scalable/places]\nSize=64\nMinSize=16\nMaxSize=512\nType=Scalable\nContext=Places\n')
    if path.exists() and path.read_text() == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        save_existing(path, home, backup)
    path.write_text(content)
