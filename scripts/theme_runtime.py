"""Apply Maya palettes and optional installed toolkit pairs without wallpaper changes."""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess


def run(argv):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=8)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def patch_ini(path, section, values, home, backup):
    """Update selected keys only; preserve unrelated settings and original formatting."""
    original = path.read_text() if path.exists() else ''
    lines = original.splitlines(keepends=True)
    remaining = dict(values)
    output = []
    inside = False
    found = False
    for line in lines:
        if line.strip().startswith('['):
            if inside:
                output.extend(f'{key}={value}\n' for key, value in remaining.items())
                remaining.clear()
            inside = line.strip() == f'[{section}]'
            found |= inside
        if inside and '=' in line and not line.lstrip().startswith(('#', ';')):
            key = line.split('=', 1)[0].strip()
            if key in remaining:
                output.append(f'{key}={remaining.pop(key)}\n')
                continue
        output.append(line)
    if remaining:
        if output and not output[-1].endswith('\n'):
            output[-1] += '\n'
        if not found:
            output.append(f'\n[{section}]\n')
        output.extend(f'{key}={value}\n' for key, value in remaining.items())
    updated = ''.join(output)
    if updated == original:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        saved = backup / path.relative_to(home)
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, saved)
    # Write through an existing user-managed link, retaining its ownership model.
    path.write_text(updated)


def toolkits(home, selected, backup):
    dark = selected == 'dark'
    config = home / '.config'
    warnings = []
    gtk_name = 'Flat-Remix-GTK-Blue-' + ('Dark' if dark else 'Light')
    theme_roots = [home / '.themes', home / '.local/share/themes', Path('/usr/local/share/themes'), Path('/usr/share/themes')]
    gtk_exists = any((root / gtk_name).is_dir() for root in theme_roots)
    if gtk_exists:
        for version in ('gtk-3.0', 'gtk-4.0'):
            patch_ini(config / version / 'settings.ini', 'Settings',
                      {'gtk-theme-name': gtk_name, 'gtk-application-prefer-dark-theme': '1' if dark else '0'}, home, backup)
    else:
        warnings.append(f'GTK theme {gtk_name} unavailable; existing GTK theme preserved')
    # Libadwaita and apps using the settings portal follow the system preference.
    if shutil.which('gsettings'):
        state = home / '.local/state/maya-dotfiles/theme-system-backup.json'
        if not state.exists():
            state.parent.mkdir(parents=True, exist_ok=True)
            saved = {}
            for key in ('gtk-theme', 'color-scheme'):
                try:
                    result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', key], capture_output=True, text=True, timeout=3)
                    if result.returncode == 0:
                        saved[key] = result.stdout.strip()
                except (OSError, subprocess.TimeoutExpired):
                    pass
            state.write_text(json.dumps(saved, indent=2) + '\n')
        if gtk_exists:
            run(['gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', gtk_name])
        if not run(['gsettings', 'set', 'org.gnome.desktop.interface', 'color-scheme', 'prefer-dark' if dark else 'prefer-light']):
            warnings.append('Desktop color-scheme preference could not be updated')
    kvantum_name = 'catppuccin-mocha-blue' if dark else 'catppuccin-latte-blue'
    kv_roots = [config / 'Kvantum', Path('/usr/share/Kvantum'), Path('/usr/local/share/Kvantum')]
    kv_exists = any((root / kvantum_name / (kvantum_name + '.kvconfig')).is_file() for root in kv_roots)
    if kv_exists:
        patch_ini(config / 'Kvantum/kvantum.kvconfig', 'General', {'theme': kvantum_name}, home, backup)
    else:
        warnings.append(f'Kvantum theme {kvantum_name} unavailable; existing Qt style preserved')
    for version in ('qt5ct', 'qt6ct'):
        scheme = config / version / 'colors' / ('Catppuccin-Mocha.conf' if dark else 'Catppuccin-Latte.conf')
        if scheme.is_file():
            values = {'custom_palette': 'true', 'color_scheme_path': str(scheme)}
            if kv_exists:
                values['style'] = 'kvantum'
            patch_ini(config / version / (version + '.conf'), 'Appearance', values, home, backup)
        elif (config / version).exists():
            warnings.append(f'{version} color scheme unavailable; existing palette preserved')
    return warnings


def signal_owned(name, sig):
    # Exact executable names, restricted to this user; never kill/restart apps.
    run(['pkill', '-' + sig, '-u', str(os.getuid()), '-x', name])


def refresh(home):
    if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
        run(['hyprctl', 'reload'])
    signal_owned('kitty', 'USR1')
    # SIGUSR2 is a config reload in the tested btop 1.4.7+; do not risk
    # terminating an older build that lacks that signal handler.
    try:
        version = subprocess.run(['btop', '--version'], capture_output=True, text=True, timeout=3)
        number = re.search(r'(\d+)\.(\d+)\.(\d+)', version.stdout)
        if number and tuple(map(int, number.groups())) >= (1, 4, 7):
            signal_owned('btop', 'USR2')
    except (OSError, subprocess.TimeoutExpired):
        pass
    run(['swaync-client', '-R'])
    run(['swaync-client', '-rs'])
    if shutil.which('tmux') and run(['tmux', 'has-session']):
        run(['tmux', 'source-file', str(home / '.tmux.conf')])
    if (home / '.local/bin/maya-lock').is_file():
        # This updates only the lockscreen cache, never the desktop image.
        run([str(home / '.local/bin/maya-lock'), '--prepare'])
    # Reload the bar last: its click handler may be the caller of this command.
    signal_owned('waybar', 'USR2')
