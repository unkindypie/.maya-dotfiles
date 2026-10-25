#!/usr/bin/env python3
"""Exercise persistent selection, recovery, clean switching, and toolkit isolation."""
from pathlib import Path
from unittest.mock import patch
import json
import os
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'scripts'))
from themes import install_profiles, mode, ALIASES
from links import backup_root
from theme_runtime import toolkits, patch_ini
from toolkit_assets import QT_ROLES, FOLDERS
import xml.etree.ElementTree as ET
import configparser

def luminance(value):
    channels = [int(value[i:i+2], 16) / 255 for i in (1, 3, 5)]
    channels = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
    return sum(a*b for a,b in zip(channels, (.2126,.7152,.0722)))

def contrast(a, b):
    x,y=sorted((luminance(a),luminance(b)))
    return (y+.05)/(x+.05)

manifest = json.loads((root / 'color-palette/palette.json').read_text())
assert manifest['default'] == 'light'
assert set(manifest['themes']['light']['colors']) == set(manifest['themes']['dark']['colors'])
for name, profile in manifest['themes'].items():
    assert f"background_tint {profile['kitty_background_tint']}" in (root / f'color-palette/profiles/{name}/kitty.conf').read_text()
    c=profile['colors']
    for fg,bg in [('novel_ink','novel_paper'),('ink','paper')]:
        assert contrast(c[fg],c[bg]) >= 7, (name, fg,bg)
    for bg in ('tmux_fill', 'tmux_accent', 'tmux_prefix', 'novel_selection'):
        assert contrast(c['novel_ink'], c[bg]) >= 4.5,(name,bg)
    active = profile['tmux_active']
    for bg in ('tmux_active_fill', active['number']):
        assert contrast(c[active['text']], c[bg]) >= 4.5, (name, 'active tab', bg)
    for fg,bg in [('muted_ink','paper'),('faint_ink','novel_paper'),('window_title_ink','paper'),('selection_ink','pink')]:
        # The existing Light faint text is intentionally retained unchanged.
        if name == 'light' and fg == 'faint_ink': continue
        assert contrast(c[fg],c[bg]) >= 4.5,(name, fg,bg,contrast(c[fg],c[bg]))
# Generated toolkit surfaces and selected text must retain readable contrast.
for name, profile in manifest['themes'].items():
    c = profile['colors']
    for fg, bg in [('ink', 'paper_white'), ('ink', 'paper_inset'),
                   ('selection_ink', 'pink'), ('window_title_ink', 'paper_inset'),
                   ('rose_ink', 'paper_white')]:
        assert contrast(c[fg], c[bg]) >= 4.5, (name, fg, bg)
    profile_dir = root / 'color-palette/profiles' / name
    qt = configparser.ConfigParser()
    qt.read(profile_dir / 'qt6.conf')
    active = [v.strip() for v in qt['ColorScheme']['active_colors'].split(',')]
    assert len(active) == len(QT_ROLES) == 22
    assert active[9] == '#ff' + c['paper_white'][1:]
    assert active[12:14] == ['#ff' + c[t][1:] for t in ('pink', 'selection_ink')]
    for icon in FOLDERS:
        for suffix in ('', '-symbolic'):
            svg = profile_dir / f'icons/scalable/places/{icon}{suffix}.svg'
            assert ET.parse(svg).getroot().tag.endswith('svg')
    for version in (3, 4):
        text = (root / f'styles/gtk{version}.css').read_text()
        import re
        assert all(token in c for token in re.findall(r'@maya_([a-z_]+)', text))

# All differences in Wofi's complete stylesheets must be in its generated header.
body=lambda text:text.split('/* END GENERATED PALETTE */',1)[1]
assert body((root/'color-palette/profiles/light/wofi.css').read_text()) == body((root/'color-palette/profiles/dark/wofi.css').read_text())

with tempfile.TemporaryDirectory(prefix='maya-themes-') as directory:
    home=Path(directory)/'home'; home.mkdir()
    env=dict(os.environ,HOME=str(home))
    env.pop('XDG_CONFIG_HOME',None)
    assert mode(home)=='light'
    assert install_profiles(root,home,backup_root(home))
    assert not install_profiles(root,home,backup_root(home))
    protected=home/'.config/mvim/init.lua';protected.parent.mkdir();protected.write_text('-- separate repository\n')
    wallpaper=home/'wallpaper.png';wallpaper.write_bytes(b'unchanged desktop image')
    before=subprocess.check_output(['git','diff','--binary'],cwd=root)
    cli=root/'home/.local/bin/maya-theme'
    def command(action):
        return subprocess.check_output([sys.executable,str(cli),action,'--no-reload'],env=env,text=True).strip()
    assert command('dark')=='dark'
    assert mode(home)=='dark'
    assert not install_profiles(root,home,backup_root(home))
    assert json.loads((home/'.config/maya-theme/palette.json').read_text())['name']=='dark'
    # A vendor replacement must recover the selected mode, not revert to Light.
    replaced=home/'.config/waybar/palette.css';replaced.unlink();replaced.write_text('vendor')
    assert install_profiles(root,home,backup_root(home))
    assert replaced.resolve()==root/'color-palette/profiles/dark/palette.css'
    assert not install_profiles(root,home,backup_root(home))
    # Reinstall must preserve the selected mode and not execute toolkit/app hooks.
    subprocess.run([sys.executable,str(root/'install.py'),'--no-services','--without-mvim','--skip-dependencies','--no-theme-apply'],env=env,check=True,stdout=subprocess.DEVNULL)
    assert mode(home)=='dark'
    # Existing installer links the personal mvim config; switching itself must not touch it.
    protected=home/'.config/mvim/init.lua'
    mvim_before=protected.read_bytes()
    assert command('toggle')=='light'
    assert command('apply')=='light'
    toggles=[subprocess.Popen([sys.executable,str(cli),'toggle','--no-reload'],env=env,stdout=subprocess.DEVNULL) for _ in range(4)]
    assert all(process.wait(timeout=5)==0 for process in toggles)
    assert mode(home)=='light'
    assert protected.read_bytes()==mvim_before
    assert wallpaper.read_bytes()==b'unchanged desktop image'
    assert subprocess.check_output(['git','diff','--binary'],cwd=root)==before
    # Check paired GTK/Qt config changes preserve unrelated settings.
    for version in ('qt5ct','qt6ct'):
        directory=home/'.config'/version; (directory/'colors').mkdir(parents=True,exist_ok=True)
        (directory/(version+'.conf')).write_text('[Appearance]\nicon_theme=mine\n[Fonts]\ngeneral=keep me\n')
    css = home / '.config/gtk-4.0/gtk.css'
    css.parent.mkdir(parents=True, exist_ok=True)
    original_css = home / 'original-gtk.css'
    original_css.write_text('/* existing user overrides */\nbutton { padding: 9px; }\n')
    css.symlink_to(original_css)
    gtk_settings = home / '.config/gtk-3.0/settings.ini'
    gtk_settings.parent.mkdir(parents=True, exist_ok=True)
    gtk_settings.write_text('[Settings]\ngtk-font-name=Keep Font 12\n')
    fake=subprocess.CompletedProcess([],0,stdout="'prefer-light'\n",stderr='')
    with patch('theme_runtime.subprocess.run',return_value=fake):
        first_backup = backup_root(home)
        assert not toolkits(home,'dark',first_backup)
        assert (first_backup / '.config/gtk-4.0/gtk.css').read_text() == '/* existing user overrides */\nbutton { padding: 9px; }\n'
        assert not css.is_symlink()
        assert original_css.read_text() == '/* existing user overrides */\nbutton { padding: 9px; }\n'
        first = css.read_text()
        assert not toolkits(home,'light',backup_root(home))
        assert not toolkits(home,'dark',backup_root(home))
        assert css.read_text() == first
        assert first.count('BEGIN MAYA THEME') == 1
        assert 'button { padding: 9px; }' in first
        assert 'gtk-font-name=Keep Font 12' in gtk_settings.read_text()
        assert json.loads((home/'.local/state/maya-dotfiles/theme-icon-base.json').read_text())['theme'] == 'mine'
    no_newline=home/'no-newline.ini'
    no_newline.write_text('[Settings]\nunrelated=value')
    patch_ini(no_newline,'Settings',{'theme':'dark'},home,backup_root(home))
    assert no_newline.read_text() == '[Settings]\nunrelated=value\ntheme=dark\n'
    qt=(home/'.config/qt6ct/qt6ct.conf').read_text()
    assert 'icon_theme=Maya-Paper-Dark' in qt and 'general=keep me' in qt and 'Maya-Paper.conf' in qt
    assert 'style=Fusion' in qt
    for variant in ('Light', 'Dark'):
        assert 'Inherits=mine' in (home/'.local/share/icons'/('Maya-Paper-'+variant)/'index.theme').read_text()
    assert not (home/'.config/Kvantum/kvantum.kvconfig').exists()
print('Light/Dark contrast, shared styles, persistent selection, recovery, clean switching and toolkit settings passed')
