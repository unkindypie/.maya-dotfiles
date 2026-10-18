# Maya dotfiles

**Neovim config: [Maya Neovim](https://github.com/unkindypie/maya-nvim/)**

Paper colors, pastels and soft pink highlights for Waybar, Kitty, tmux and Zsh.
Works with KooL Fedora Hyprland; the main desktop components also work without KooL.

## Install

Install Git, Python 3, Zsh, Kitty, tmux, Waybar, fzf and a Nerd Font-capable
Wayland desktop first. Fonts are bundled. For the bar controls, install
`rofi-wayland`, `brightnessctl`, `wireplumber`, `pavucontrol`, `nm-connection-editor`
and `playerctl`. SwayNC, lsd and fastfetch are optional. Install hyprlock and hypridle for screen locking.

```sh
cd ~/.maya-dotfiles
python3 install.py
```

The installer backs up replaced files and asks whether to install Maya Neovim.
Use `--with-mvim` or `--without-mvim` to choose explicitly. Maya Neovim has its
own dependency installer, which may ask for sudo or additional choices.

Missing Oh My Zsh and tmux plugins download at the revisions in dependencies.json.
Existing installations and local changes are preserved. A fresh install needs
internet; use `--skip-dependencies` for an offline install with dependencies ready.

## Edit your configs

Installed files are symlinks into `home/`: editing either location changes the
same file. Reload the application afterward. Run the installer to link new files.

- **Kitty:** `~/.config/kitty/kitty.conf`; paper texture/tint in
  `~/.local/share/kitty-personal/notebook.conf`.
- **Wofi:** `~/.config/wofi/config` and `style.css`: paper panels, a pink search
  strip, beveled rows and crisp offset shadows. Preview with `wofi --show drun`.
  This is an optional alternative; Super+D uses the familiar Rofi launcher.
- **Rofi:** `~/.config/rofi/themes/maya-paper.rasi` keeps KooL Style 4’s layout
  with a slim classic-macOS-style frame, cat icon, right-hand rose dot,
  paper surfaces and dusty pink selections.
  Super+D preserves usage history/ranking and the apps/files/term/window tabs.
  It has no KooL or
  Wallust dependency. Applies to the main launcher; KooL’s separate menus keep
  their own themes.
- **Wallpaper (KooL):** press **Super+W** to open the wallpaper picker. It reads
  `~/Pictures/wallpapers/` (including subfolders), or `wallpapers/` inside your
  XDG Pictures directory if customized. Add images there to list them in the picker.
- **Lock/idle:** `~/.config/hypr/hyprlock.conf` and `hypridle.conf`. A layered 90s-style dialog,
  beveled pink title bar and blurred current wallpaper; **Super+B** or `~/.local/bin/maya-lock` locks.
  Wallpaper follows awww/swww, Waypaper, then KooL’s cache, with plain paper as
  fallback. Private wallpaper images stay outside Git. The idle warning remains
  at 9 minutes and locking at 10; display-off/suspend stay disabled. KooL already
  starts hypridle; on another setup add `exec-once = hypridle`. Restart hypridle
  after changing idle settings. Weather has its own bottom-left card; battery and
  uptime share a bottom-right card. Both have pastel title strips and crisp offset shadows. The login dialog has
  a backing sheet, recessed clock display and soft pink password field. Long weather text wraps to fit. Weather
  refreshes in the background using KooL’s existing provider when present;
  otherwise wttr.in uses your approximate IP location. Cached weather stays
  available offline and is marked when stale. No location/cache data is committed.
- **SwayNC:** `~/.config/swaync/`: opaque paper cards, a cat title strip,
  rose controls and beveled borders. Reload with `swaync-client -R` and
  `swaync-client -rs`. Quick actions retain KooL integrations; locking uses Maya lock.
- **Waybar:** `~/.config/waybar/config` and `style.css`.
- **tmux:** `~/.tmux.conf`; set `@theme_mode` in `~/.tmux.theme.conf` to `light`
  or `dark`, then press Ctrl-b r. Light mode uses a compact single-row bar with rounded ends.
- **Zsh:** `~/.config/zsh/shared.zsh`. The local `~/.zshrc` loads this plus private
  `secrets.zsh` and machine-specific `local.zsh` in the same directory.
  Secrets stay outside Git with permissions 600. Recognized credential
  assignments are migrated during installation; move multiline secrets manually.
- **Maya Neovim:** `~/.config/mvim/init.lua` is a personal override, not a complete
  Neovim distribution. Install the linked Maya Neovim project to use it.
- **Screenshots:** Hyprshot captures into Swappy for highlighting and annotation.
  Super+S selects a region; existing Print shortcuts also open the editor.
  Nothing is saved automatically. In Swappy use Ctrl+C to copy, Ctrl+S to save,
  or Escape to discard. Requires `hyprshot` and `swappy`.
- **Hyprland:** `~/.config/hypr/hyprland.lua` is the active entry point.
  It loads installed KooL Lua modules when available, then our native Lua
  `UserConfigs/user_*.lua` overrides. Without KooL it provides basic terminal,
  close-window and workspace bindings before loading the personal settings.
  `user_startup.lua` launches Vesktop, Telegram, Chrome with its last session on
  workspace 1, and one Kitty on workspace 2. Startup runs only at login.
  Vesktop opens on workspace 3; later Kitty windows stay on the current workspace.
  Edit `user_keybinds.lua` for shortcuts, `user_window_rules.lua` for workspace
  assignments, `user_settings.lua` for input settings, and `monitors.lua` for displays.
  Personal settings retain this laptop’s monitor and keyboard choices.
  Some shortcuts require KooL scripts, Chrome, Thunar or hyprshot.
  Appearance is in `user_decorations.lua`, animation timing in `user_animations.lua`:
  uniform 3px pastel borders, fixed gradient directions, layered brown shadows,
  and no inactive dimming. Windows fade over 600 ms from 90% compositor opacity
  when unfocused to fully solid when focused. Unfocused windows retain app alpha
  and background blur at size 8/3 passes; the app-alpha override switches immediately.
  Reload with `hyprctl reload`. Shared colors still come from the palette generator.

The old `.conf` Hyprland files remain as rollback references; the Lua entry point
never sources them. Hyprlock and Hypridle still use their own `.conf` formats.
Hyprland 0.56 supports switching an existing session with `hyprctl reload full-reset`
after installing the Lua entry point. Normal edits only need `hyprctl reload`.
For rollback, remove the installed `hyprland.lua` symlink and run
`hyprctl reload full-reset` to use the preserved `hyprland.conf` again. Disable
`maya-dotfiles.path` first so link recovery does not restore the Lua entry point.
Back up custom configs before installation; the installer also backs up files it replaces.

## KooL integration and protection

Waybar optionally shows KooL's help, settings and blue-light filter buttons when
their scripts and applications exist. Otherwise they hide. The network button
opens NetworkManager's GUI. Original KooL Waybar files are archived in reference/.

`maya-waybar.service` runs the bar; `waybar.service` aliases it so KooL startup
and refresh use the same instance. The installer and link recovery also patch
KooL’s dropdown discovery to match only its dedicated terminal class, preventing
it from hiding another app during login. Original scripts are backed up; upstream
source trees are not stored here.

`maya-dotfiles.path` repairs replaced
Kitty, Waybar, Rofi, Wofi, SwayNC and Hyprland user-config symlinks. Vendor writes *through* a symlink
also change the repo: inspect `git diff` after theme tools. Keep this repo in
place. Backups live in `~/.local/state/maya-dotfiles/backups/`.

```sh
# Disable the managed bar and link recovery:
systemctl --user disable --now maya-dotfiles.path maya-waybar.service
```

Without systemd, install with `--no-services` and start
`~/.local/bin/maya-waybar` from Hyprland. Automatic recovery requires systemd.
Disable other Waybar launchers if they create duplicate bars.

## Checks

```sh
python3 tests/check.py
python3 tests/check-dependencies.py
git diff --check
```

See ATTRIBUTION.md for asset sources and licenses.

## Shared colors

Edit [`color-palette/palette.json`](color-palette/palette.json) in the repo root.
The installed `~/.config/maya-theme/` files link to `color-palette/`. Different paper,
pink and app-specific shades have separate names; no colors are forced to match.
Exact duplicates and unreviewed near-duplicates are rejected. A conservative
Oklab distance check (<0.02) flags similar opaque shades. Two documented
exceptions preserve terminal white versus warm paper and lavender versus pink;
alpha variants remain separate. Run `python3 scripts/generate-palette.py --audit`
to review them. The palette has 59 colors, reduced from 80.
It supplies Waybar, Wofi, Rofi, SwayNC, Hyprlock, Hyprland and Kitty's personal Novel theme.

```sh
python3 scripts/generate-palette.py
```

This updates small native include files (and Wofi’s generated color header),
not whole config templates. Wofi needs an inline header because its CSS imports
resolve from the launch directory. Layouts
remain directly editable. The installer also regenerates these files. Reload
Waybar/Hyprland, restart Kitty or reload its config, and reopen launchers/the locker
to apply. `python3 scripts/generate-palette.py --check` checks for stale includes.
Edit the palette rather than generated files. Other Kitty themes, Wallust output,
and tmux/mvim's separate palettes are unchanged. Palette values do not recolor
the wallpaper or texture image itself.
