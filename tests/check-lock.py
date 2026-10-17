#!/usr/bin/env python3
"""Check wallpaper selection/fallback without invoking the screen locker."""
from pathlib import Path
from unittest.mock import patch
import os, runpy, tempfile
root = Path(__file__).resolve().parents[1]
lock = runpy.run_path(str(root / 'home/.local/bin/maya-lock'))
with tempfile.TemporaryDirectory() as d, patch('shutil.which', return_value=None):
    home = Path(d)
    with patch.dict(os.environ, HOME=d):
        fallback = lock['prepare'](home)
        assert fallback.is_symlink()
        assert fallback.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
        wallpaper = home / 'My Wallpaper.png'
        wallpaper.write_bytes(fallback.read_bytes())
        config = home / '.config/waypaper/config.ini'
        config.parent.mkdir(parents=True)
        config.write_text('[Settings]\nwallpaper = ' + str(wallpaper) + '\n')
        assert lock['choose_wallpaper'](home) == wallpaper
        assert lock['prepare'](home).resolve() == wallpaper
        config.unlink()
        kool = home / '.config/hypr/wallpaper_effects/.wallpaper_current'
        kool.parent.mkdir(parents=True)
        kool.symlink_to(wallpaper)
        assert lock['choose_wallpaper'](home) == wallpaper
print('Waypaper, KooL fallback and plain-paper background checks passed; no lock invoked')
