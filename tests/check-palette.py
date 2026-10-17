#!/usr/bin/env python3
"""Check native palette output, coverage, reproducibility, and input validation."""
from pathlib import Path
import copy, json, re, runpy, tempfile, shutil, subprocess
root = Path(__file__).resolve().parents[1]
render = runpy.run_path(str(root / 'scripts/generate-palette.py'))['render']
outputs = render(root)
for name, content in outputs.items():
    assert (root / name).read_text() == content, f'Stale palette: {name}'
colors = json.loads((root / 'color-palette/palette.json').read_text())['colors']
for name in ['home/.config/swaync/style.css','home/.config/waybar/style.css','home/.config/wofi/style.css','home/.config/rofi/themes/maya-paper.rasi','home/.config/hypr/hyprlock.conf','home/.config/hypr/maya-appearance.conf']:
    text = (root / name).read_text()
    for token in re.findall(r'[@$]maya[_-]([a-z0-9_-]+)', text):
        token = token.replace('-', '_')
        assert token in colors or token in ('password_placeholder','password_failure','title_gradient'), (name, token)
with tempfile.TemporaryDirectory() as d:
    temp = Path(d)
    palette = temp / 'color-palette/palette.json'
    palette.parent.mkdir(parents=True)
    wofi = temp / 'home/.config/wofi/style.css'
    wofi.parent.mkdir(parents=True)
    wofi.write_text('/* editable layout */\n')
    data = json.loads((root / 'color-palette/palette.json').read_text())
    changed = copy.deepcopy(data)
    changed['colors']['paper'] = '#010203'
    palette.write_text(json.dumps(changed))
    result = render(temp)
    assert '@define-color maya_paper #010203;' in result['home/.config/waybar/palette.css']
    assert '$maya_paper = rgb(010203)' in result['color-palette/colors.conf']
    assert 'maya-paper: #010203;' in result['home/.config/rofi/themes/maya-palette.rasi']
    assert 'paper = "rgb(010203)"' in result['color-palette/colors.lua']
    changed['colors']['paper'] = changed['colors']['paper_white']
    palette.write_text(json.dumps(changed))
    try: render(temp)
    except ValueError: pass
    else: raise AssertionError('Duplicate palette colors accepted')
    changed['colors']['paper'] = '#fffbf3'
    palette.write_text(json.dumps(changed))
    try: render(temp)
    except ValueError: pass
    else: raise AssertionError('Unreviewed near-duplicate palette colors accepted')
    changed['colors']['paper'] = 'not a color'
    palette.write_text(json.dumps(changed))
    try: render(temp)
    except ValueError: pass
    else: raise AssertionError('Invalid palette accepted')
print('Palette coverage, native formats, regeneration and invalid-input checks passed')

# Rofi can exit successfully from dump-theme even after a parse error. Use its
# effective theme with a self-contained import, without displaying a launcher.
if shutil.which('rofi'):
    with tempfile.TemporaryDirectory() as d:
        theme = Path(d) / 'theme.rasi'
        text = (root / 'home/.config/rofi/themes/maya-paper.rasi').read_text()
        text = text.replace('~/.config/rofi/themes/maya-palette.rasi',
                            str(root / 'home/.config/rofi/themes/maya-palette.rasi'))
        theme.write_text(text)
        result = subprocess.run(['rofi', '-no-config', '-theme', str(theme), '-dump-theme'], capture_output=True, text=True)
        assert result.returncode == 0 and 'titlebar {' in result.stdout and 'maya-paper:' in result.stdout and 'Applications' in result.stdout, result.stdout + result.stderr
    print('Rofi effective theme contains the shared palette and custom titlebar')
