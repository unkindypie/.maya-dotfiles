# Light and Dark themes

Maya uses one set of component styles, with two generated color profiles.
**Light** is the default and retains the original paper/pastel colors.
**Dark** uses warm charcoal surfaces, cream text and pastel accents. The selected
mode persists across login, link repair and reinstall.

## Switching

The `day`/`night` button beside the Waybar settings button toggles modes. The tooltip
names the current mode and the mode selected by clicking. The same command works
without KooL or Waybar:

```sh
maya-theme light
maya-theme dark
maya-theme toggle
maya-theme status
maya-theme apply
```

`apply` reloads the selected theme after palette edits. `status --json` provides
Waybar output. Add `--no-reload` to a selection command to update only palette
links, without changing toolkit preferences or sending app reload commands. Apps that
watch the selected profile, including mvim, can still respond automatically.

There is no time-of-day or wallpaper-based switching. KooL's **Switch Dark-Light
Theme** menu delegates to this switch instead of its wallpaper-changing script.
Other explicit KooL wallpaper controls remain independent.

## Editing colors and styles

Edit `themes.light.colors` or `themes.dark.colors` in
[`color-palette/palette.json`](../color-palette/palette.json). Both contain the same
semantic token names; app mappings are shared. Add documented per-mode
`similarity_exceptions` only for distinct app roles that need similar colors.
The generator rejects exact duplicates and unreviewed near-duplicates.

```sh
python3 scripts/generate-palette.py
python3 scripts/generate-palette.py --check
python3 scripts/generate-palette.py --audit
maya-theme apply
```

Generated profiles live in `color-palette/profiles/light/` and `dark/`.
`~/.config/maya-theme/profiles` links there, and `current` selects one profile.
Application palette links point through `current`; switching replaces only this
local selector, not tracked files. Earlier generated Light outputs remain as
compatibility/reference artifacts; they are not the active runtime selection.
Do not edit generated files directly.

Shared component styles remain in `home/`. Wofi needs a complete stylesheet with
an inline palette: edit [`styles/wofi.css`](../styles/wofi.css), then regenerate.
Both generated Wofi stylesheets contain exactly the same layout body.

## Coverage and live updates

- Waybar, Kitty, SwayNC, Hyprland, btop 1.4.7+ and the default tmux server reload
  through their supported interfaces. Sessions and apps are not terminated.
- Rofi, Wofi and Hyprlock read the selected profile when next opened. Existing
  launchers or an already displayed lockscreen may need reopening.
- Kitty retains its notebook texture, opacity and focus animation. Dark uses a
  stronger background-color tint (`0.78`, versus Light’s original `0.35`) so the
  notebook lines remain subtle behind text. Adjust `kitty_background_tint` in
  each palette profile to tune this. tmux uses the
  same rounded status layout in both modes; btop keeps its CPU/GPU layout.
- Zsh prompt colors, syntax highlighting and fzf colors refresh at the next prompt.
  After first installing this feature, existing shells need reopening once to load
  the new prompt hook. Additional custom tmux servers pick up colors on config reload.
- mvim keeps its colorscheme in its own repository. The personal `theme_background`
  option reads the selected profile at startup, and a watcher updates open editors
  when the mode changes. No editor restart or per-switch config rewrite is needed.
  A transparent editor naturally reveals its terminal background. Existing editors
  need the integration loaded once, or reopening, after first installing it.
- Desktop wallpaper image, path, daemon, and transitions are never changed by
  `maya-theme`. The lockscreen continues to use the existing wallpaper.

## GTK, Qt and applications

Desktop apps use generated **Maya Paper** themes from the same palette as Waybar
and the terminal. Light uses cream paper and brown text; Dark uses warm charcoal
and cream text. Both use pink selections and sage/lavender accents with identical
widget geometry.

| Integration | Light | Dark |
| --- | --- | --- |
| GTK 3 / Thunar | Maya-Paper-Light | Maya-Paper-Dark |
| GTK 4 / libadwaita | Maya Light surface/accent colors | Maya Dark surface/accent colors |
| Qt5ct / Qt6ct | Maya Light palette, Fusion controls | Maya Dark palette, Fusion controls |
| Folder icon overlay | Maya-Paper-Light | Maya-Paper-Dark |
| Desktop / portal preference | prefer-light | prefer-dark |

Editable widget styles are `styles/gtk3.css` and `styles/gtk4.css`; original folder
artwork is `styles/folder.svg`. Regenerate after editing them. GTK 3 wraps the
system GTK Adwaita foundation; no upstream theme source tree is bundled. GTK 4
uses its native foundation and libadwaita surface/accent variables. The generated
GTK 4 import is added to `~/.config/gtk-4.0/gtk.css` inside a marked Maya block;
existing user rules are backed up and retained after that import, keeping their
precedence. `maya-theme apply` repairs a missing import.

Qt palettes include the color roles for each Qt version. Qt5ct and Qt6ct provide
the platform integrations; install the one needed by your apps. The Hyprland
config clears KooL's forced Kvantum style and selects `qt5ct` as the platform
key (also supported by qt6ct). Qt settings select Fusion, leaving installed
Kvantum themes untouched. Existing terminal sessions can retain the old Qt
environment; reopen them before launching Qt apps from those shells. Outside
Hyprland, configure `QT_QPA_PLATFORMTHEME=qt5ct` in your session and remove any
`QT_STYLE_OVERRIDE` that forces another style.

The original pastel folder SVGs include common special folders and open-folder
variants. Other icons inherit the original icon theme, remembered once in
`~/.local/state/maya-dotfiles/theme-icon-base.json`. Application icons and the
original icon installation are preserved; switching never makes Maya themes
inherit one another.

Fonts, scaling and unrelated toolkit preferences are preserved. Replaced settings
are backed up. No third-party theme download is required. Missing generated assets
are reported rather than replaced with an unrelated theme. GTK apps that follow
settings notifications can update live; GTK 4 user stylesheets and some Qt apps
need reopening. Flatpak/sandboxed apps or apps with explicit internal themes may
not follow host styles. No app is forcibly restarted.

## Vencord / Vesktop system24

When an existing Vencord or Vesktop installation is found, `maya-theme apply`
installs pinned, self-contained copies of refact0r's `system24.theme.css` and
`system24-light.theme.css`. Existing copies are backed up first. Their system24
and midnight layout CSS is bundled in this repo under MIT, with upstream notices;
revisions and artifact hashes are recorded in `dependencies.json`. Only theme
artifacts are included, not upstream source trees. Optional upstream web fonts
still need network access; optional font/image asset URLs are revision-pinned.

Enable either **system24** entry in Vencord's Local Themes and enable **QuickCSS**.
Your currently enabled entry stays checked: Maya selects the upstream Light/Dark
colors using a marked `MAYA SYSTEM24 MODE` block in `settings/quickCss.css`.
This changes the actual appearance live through Vencord's built-in file watcher,
without restarting Discord or changing its settings JSON. It keeps system24's
own colors rather than recoloring it with the Maya app palette.

Other themes, plugin settings, theme links, and QuickCSS outside that block are
preserved. If neither system24 entry is enabled, the switch removes its own color
override and leaves other themes alone. With QuickCSS disabled it reports the
needed setting instead of enabling it silently. `--no-reload` skips this app
integration too. Client directories are not created on machines without Vencord.
The integration recognizes standard `vesktop`, `Vencord`, and `vencord` config
folders plus Flatpak Vesktop's config folder.

QuickCSS writes retain the existing file inode so Vencord keeps watching after
repeated switches. If QuickCSS was a symlink, the original link is backed up and
the amended file is materialized without editing the link target; reopen the
client once in that case to attach its watcher to the new file. Theme application
repairs replaced system24 files, preserving unrelated themes.

## Installation, protection and recovery

Fresh installs select Light; reinstall preserves a valid existing selection.
`install.py --no-theme-apply` installs links without applying toolkit settings or
reloading running apps. `maya-theme apply` can apply them later.

Replaced configs and changed toolkit settings are backed up beneath
`~/.local/state/maya-dotfiles/backups/`. The original desktop preference values
are recorded in `~/.local/state/maya-dotfiles/theme-system-backup.json` before
first applying system settings. Use `maya-theme light` to return to the default.

Link recovery repairs aliases without resetting the selected mode. As with other
managed configs, a vendor write *through* a symlink can still modify its target:
inspect `git diff` after KooL/Wallust tools. The selector does not prevent vendor
writes; it prevents normal theme switching from changing tracked files.

[Back to README](../README.md)
