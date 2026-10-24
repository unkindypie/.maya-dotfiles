"""Generate original toolkit overrides, Qt color roles and folder icon overlays."""
from string import Template

# QPalette::ColorRole order, including Qt6 PlaceholderText and Accent.
QT_ROLES = ('ink', 'paper', 'paper_white', 'border', 'paper_inset', 'muted_ink',
            'ink', 'ink', 'ink', 'paper_white', 'paper', 'border', 'pink',
            'selection_ink', 'rose_ink', 'lavender_ink', 'paper_white', 'ink',
            'paper_inset', 'ink', 'muted_ink', 'pink')
FOLDERS = {
    'folder': '', 'folder-open': '',
    'folder-documents': '<path d="M26 34H37V47H26Z M29 38H34 M29 42H34"/>',
    'folder-download': '<path d="M32 33V44 M27 40L32 45L37 40 M25 48H39"/>',
    'folder-pictures': '<path d="M24 34H40V47H24Z M25 45L30 39L34 43L37 40L40 44"/>',
    'folder-music': '<path d="M30 45V34L39 32V43 M30 35L39 33"/><circle cx="27" cy="46" r="3"/><circle cx="36" cy="44" r="3"/>',
    'folder-videos': '<path d="M25 34H40V47H25Z M31 37L36 40L31 44Z"/>',
    'folder-desktop': '<path d="M24 33H40V44H24Z M32 44V48 M28 48H36"/>',
    'folder-publicshare': '<circle cx="27" cy="37" r="3"/><circle cx="37" cy="43" r="3"/><path d="M24 46Q26 40 30 43 M34 49Q36 44 40 47"/>',
    'folder-templates': '<path d="M26 33H38V47H26Z M29 37H35 M29 41H35"/>',
    'user-home': '<path d="M24 40L32 33L40 40 M27 39V48H37V39 M31 48V43H34V48"/>',
}


def render(root, mode, colors, css_header):
    prefix = f'color-palette/profiles/{mode}/'
    output = {}
    name = 'Maya-Paper-' + mode.title()
    for version in (3, 4):
        body = (root / f'styles/gtk{version}.css').read_text()
        output[prefix + f'gtk{version}.css'] = css_header + body
        resource = ('Adwaita/gtk-contained' + ('-dark' if mode == 'dark' else '')
                    if version == 3 else 'Default/Default-' + mode)
        output[prefix + f'gtk-theme/gtk-{version}.0/gtk.css'] = (
            f'@import url("resource:///org/gtk/libgtk/theme/{resource}.css");\n'
            + css_header + body)
    output[prefix + 'gtk-theme/index.theme'] = f'[Desktop Entry]\nName={name}\nType=X-GNOME-Metatheme\n[X-GNOME-Metatheme]\nGtkTheme={name}\n'
    for version, count in ((5, 21), (6, 22)):
        qt = '[ColorScheme]\n'
        for group in ('active', 'disabled', 'inactive'):
            roles = list(QT_ROLES[:count])
            if group == 'disabled':
                for index in (0, 6, 7, 8, 19):
                    roles[index] = 'window_title_ink'
            qt += group + '_colors=' + ', '.join('#ff' + colors[token][1:] for token in roles) + '\n'
        output[prefix + f'qt{version}.conf'] = qt
    template = Template((root / 'styles/folder.svg').read_text())
    for icon, glyph in FOLDERS.items():
        front = ('M12 24H59L53 50Q52 54 48 54H10Z' if icon == 'folder-open'
                 else 'M6 23H58V50Q58 54 54 54H10Q6 54 6 50Z')
        output[prefix + f'icons/scalable/places/{icon}.svg'] = template.substitute(colors, front=front, glyph=glyph)
    # Symbolic icons follow the requesting widget's foreground color.
    for icon in FOLDERS:
        output[prefix + f'icons/scalable/places/{icon}-symbolic.svg'] = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">'
            '<path fill="currentColor" d="M1 3h6l2 2h6v9H1Z"/></svg>\n')
    return output
