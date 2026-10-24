"""Keep enabled system24 themes pinned and follow Maya via Vencord's QuickCSS watcher."""
from pathlib import Path
import hashlib
import json
import re
from links import save_existing

FILENAMES = {'light': 'system24-light.theme.css', 'dark': 'system24.theme.css'}
START = '/* BEGIN MAYA SYSTEM24 MODE */'
END = '/* END MAYA SYSTEM24 MODE */'


def artifacts(root):
    """Verify bundled release artifacts against the pinned dependency manifest."""
    manifest = json.loads((root / 'dependencies.json').read_text())['theme_artifacts']
    for name, spec in manifest.items():
        for filename, expected in spec['sha256'].items():
            data = (root / 'assets/themes' / name / filename).read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f'Changed pinned theme artifact: {name}/{filename}')
    return manifest


def without_imports(text):
    # Upstream imports are single lines; URLs may themselves contain semicolons.
    return '\n'.join(line for line in text.splitlines() if not line.strip().startswith('@import ')) + '\n'


def bundled_theme(root, mode, manifest):
    base = root / 'assets/themes'
    theme = (base / 'system24' / FILENAMES[mode]).read_text()
    midnight = (base / 'midnight-discord/midnight.css').read_text()
    system = (base / 'system24/system24.css').read_text()
    header, options = theme.split('*/', 1)
    licenses = ''.join('\n/* ' + (base / name / 'LICENSE').read_text() + ' */\n'
                       for name in ('system24', 'midnight-discord'))
    imports = '\n'.join(line for text in (midnight, system) for line in text.splitlines()
                        if line.startswith('@import ') and 'fonts.googleapis.com' in line) + '\n'
    css = (header + '*/\n/* Maya: bundled pinned CSS; upstream options retained. */\n'
           + licenses + imports + without_imports(midnight) + without_imports(system)
           + without_imports(options))
    for name in ('system24', 'midnight-discord'):
        # Pin optional upstream font/image assets too, without bundling their binaries.
        sha = manifest[name]['commit']
        css = css.replace(f'https://refact0r.github.io/{name}/assets/',
                          f'https://raw.githubusercontent.com/refact0r/{name}/{sha}/assets/')
        css = css.replace(f'https://raw.githubusercontent.com/refact0r/{name}/refs/heads/main/',
                          f'https://raw.githubusercontent.com/refact0r/{name}/{sha}/')
    return css


def mode_css(root, mode):
    text = (root / 'assets/themes/system24' / FILENAMES[mode]).read_text()
    colors = text.split('/* color options */', 1)[1].strip()
    colors = colors.replace(':root {', f':root:root {{\n    color-scheme: {mode};', 1)
    return START + f'\n/* system24 by refact0r (MIT); Maya mode: {mode}. */\n' + colors + '\n' + END


def write_changed(path, content, home, backup):
    if path.is_file() and path.read_text() == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        save_existing(path, home, backup)
        if path.is_symlink():
            # Never write through a user link into another repository or theme.
            path.unlink()
    # Keep the inode: Vencord watches QuickCSS itself, not just its directory.
    # Its debounced watcher reads after this short, synchronous write completes.
    with path.open('w') as stream:
        stream.write(content)


def apply(root, home, mode, backup):
    candidates = [home / '.config' / name for name in ('vesktop', 'Vencord', 'vencord')]
    candidates.append(home / '.var/app/dev.vencord.Vesktop/config/vesktop')
    warnings = []
    manifest = None
    for client in candidates:
        settings_path = client / 'settings/settings.json'
        if not settings_path.is_file():
            continue
        try:
            settings = json.loads(settings_path.read_text())
        except (OSError, ValueError):
            warnings.append(f'{client.name}: cannot read Vencord settings; theme preserved')
            continue
        if manifest is None:
            manifest = artifacts(root)
        for variant, filename in FILENAMES.items():
            write_changed(client / 'themes' / filename, bundled_theme(root, variant, manifest), home, backup)
        enabled = settings.get('enabledThemes', [])
        quick = client / 'settings/quickCss.css'
        original = quick.read_text() if quick.exists() else ''
        if not any(filename in enabled for filename in FILENAMES.values()):
            if START in original and END in original:
                cleaned = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', original, flags=re.S)
                write_changed(quick, cleaned, home, backup)
            warnings.append(f'{client.name}: enable either bundled system24 theme, then run maya-theme apply')
            continue
        if not settings.get('useQuickCss', False):
            warnings.append(f'{client.name}: enable QuickCSS to let system24 follow Maya mode')
            continue
        was_link = quick.is_symlink()
        block = mode_css(root, mode)
        if START in original and END in original:
            updated = re.sub(re.escape(START) + r'.*?' + re.escape(END),
                             lambda _: block, original, flags=re.S)
        else:
            updated = original + ('\n' if original and not original.endswith('\n') else '') + block + '\n'
        write_changed(quick, updated, home, backup)
        if was_link:
            warnings.append(f'{client.name}: reopen once to watch the materialized QuickCSS file')
    return warnings
