#!/usr/bin/env python3
"""Check pinned system24 CSS, live-watcher writes, preservation and optional clients."""
from pathlib import Path
import json
import re
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from vencord_theme import apply, artifacts, bundled_theme, mode_css, START, END
from links import backup_root

root = Path(__file__).resolve().parents[1]
manifest = artifacts(root)
for mode in ('light', 'dark'):
    css = bundled_theme(root, mode, manifest)
    assert 'Copyright (c) 2025 refact0r' in css and 'MIT License' in css
    assert 'github.io' not in css and 'refs/heads/main' not in css
    assert not any('system24.css' in line or 'midnight.css' in line
                   for line in css.splitlines() if line.strip().startswith('@import'))
    assert '--ascii-loader: system24' in css
    assert ':root:root' in mode_css(root, mode)
    assert f'color-scheme: {mode};' in mode_css(root, mode)

with tempfile.TemporaryDirectory(prefix='maya-vencord-') as directory:
    home = Path(directory)
    assert not apply(root, home, 'dark', backup_root(home))
    assert not (home / '.config').exists(), 'Do not create an unused client'
    for name in ('vesktop', 'Vencord'):
        client = home / '.config' / name
        settings = client / 'settings/settings.json'
        settings.parent.mkdir(parents=True)
        data = {'useQuickCss': True, 'enabledThemes': ['system24-light.theme.css', 'unrelated.css'],
                'plugins': {'SomePlugin': {'enabled': True}}, 'themeLinks': ['https://example.org/keep.css']}
        settings.write_text(json.dumps(data, indent=4))
        before = settings.read_bytes()
        quick = settings.parent / 'quickCss.css'
        user_css = '/* personal */\nbody { --font: monospace; }\n'
        quick.write_text(user_css)
        inode = quick.stat().st_ino
        old_theme = client / 'themes/system24-light.theme.css'
        old_theme.parent.mkdir(); old_theme.write_text('/* existing local theme */')
        backup = backup_root(home)
        assert not apply(root, home, 'dark', backup)
        assert (backup / old_theme.relative_to(home)).read_text() == '/* existing local theme */'
        assert settings.read_bytes() == before
        assert quick.stat().st_ino == inode
        assert quick.read_text().startswith(user_css)
        assert 'Maya mode: dark' in quick.read_text()
        first = quick.read_bytes()
        assert not apply(root, home, 'dark', backup_root(home))
        assert quick.read_bytes() == first
        assert not apply(root, home, 'light', backup_root(home))
        assert quick.read_text().count(START) == quick.read_text().count(END) == 1
        assert quick.stat().st_ino == inode
        assert settings.read_bytes() == before
        data['enabledThemes'] = ['unrelated.css']
        settings.write_text(json.dumps(data))
        assert apply(root, home, 'light', backup_root(home))
        assert quick.read_text() == user_css
        data['enabledThemes'] = ['system24.theme.css']; data['useQuickCss'] = False
        settings.write_text(json.dumps(data))
        assert apply(root, home, 'dark', backup_root(home))
        assert quick.read_text() == user_css
        # Existing links are backed up and materialized, not written through.
        target = home / (name + '-custom.css'); target.write_text(user_css)
        quick.unlink(); quick.symlink_to(target)
        data['useQuickCss'] = True; settings.write_text(json.dumps(data))
        assert apply(root, home, 'dark', backup_root(home))
        assert not quick.is_symlink() and target.read_text() == user_css
print('Pinned system24 artifacts, both modes, client isolation, settings preservation and QuickCSS watcher writes passed')
