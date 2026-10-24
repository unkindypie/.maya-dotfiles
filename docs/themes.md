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
- Kitty retains its notebook texture, opacity and focus animation. tmux uses the
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

The custom Maya components use only palette changes. For other apps, the switch
selects matching installed toolkit themes:

| Integration | Light | Dark |
| --- | --- | --- |
| GTK | Flat-Remix-GTK-Blue-Light | Flat-Remix-GTK-Blue-Dark |
| Qt5ct / Qt6ct palette | Catppuccin-Latte | Catppuccin-Mocha |
| Kvantum | catppuccin-latte-blue | catppuccin-mocha-blue |
| Desktop / portal preference | prefer-light | prefer-dark |

These installed theme assets remain outside this repository. Fonts, icons and
unrelated toolkit preferences are preserved. If an asset is missing, the switch
reports the unavailable integration and preserves its previous setting; it does
not download or replace theme installations. Apps following the system preference
can update live; others need reopening. An app with an explicit internal theme
may override the system choice. No app is forcibly restarted.

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
