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
- **Rofi:** `~/.config/rofi/themes/maya-paper.rasi` keeps KooL Style 4’s layout
  with paper surfaces, dusty pink selections and rose borders. It has no KooL or
  Wallust dependency. Applies to the main launcher; KooL’s separate menus keep
  their own themes.
- **Lock/idle:** `~/.config/hypr/hyprlock.conf` and `hypridle.conf`. A cream card,
  rose outlines and blurred current wallpaper; **Super+B** or `~/.local/bin/maya-lock` locks.
  Wallpaper follows awww/swww, Waypaper, then KooL’s cache, with plain paper as
  fallback. Private wallpaper images stay outside Git. The idle warning remains
  at 9 minutes and locking at 10; display-off/suspend stay disabled. KooL already
  starts hypridle; on another setup add `exec-once = hypridle`. Restart hypridle
  after changing idle settings.
- **Waybar:** `~/.config/waybar/config` and `style.css`.
- **tmux:** `~/.tmux.conf`; set `@theme_mode` in `~/.tmux.theme.conf` to `light`
  or `dark`, then press Ctrl-b r.
- **Zsh:** `~/.config/zsh/shared.zsh`. The local `~/.zshrc` loads this plus private
  `secrets.zsh` and machine-specific `local.zsh` in the same directory.
  Secrets stay outside Git with permissions 600. Recognized credential
  assignments are migrated during installation; move multiline secrets manually.
- **Maya Neovim:** `~/.config/mvim/init.lua` is a personal override, not a complete
  Neovim distribution. Install the linked Maya Neovim project to use it.
- **Hyprland:** `~/.config/hypr/UserConfigs/` contains your custom hotkeys and
  settings. Focus appearance is in `~/.config/hypr/maya-appearance.conf`:
  full compositor opacity, no inactive dimming, 4px rose focus borders, 2px taupe inactive borders and
  soft brown shadows (stronger when focused). Backdrop blur stays at size 8/3 passes.
  Reload with `hyprctl reload`. Kitty's own background opacity still applies.

KooL already loads UserConfigs. On a non-KooL Hyprland setup, add near the end of
your config:

```conf
source = ~/.config/hypr/maya-appearance.conf
# Optional personal hotkeys/workspace assignments:
source = ~/.config/hypr/UserConfigs/UserKeybinds.conf
```

The other UserConfigs preserve this laptop's settings and KooL integrations;
do not source them all on an unrelated machine. Some hotkeys need Chrome,
Thunar or hyprshot. Obsidian tmux popups require your own Neovim Obsidian setup.

## KooL integration and protection

Waybar optionally shows KooL's help, settings and blue-light filter buttons when
their scripts and applications exist. Otherwise they hide. The network button
opens NetworkManager's GUI. Original KooL Waybar files are archived in reference/.

`maya-waybar.service` runs the bar; `maya-dotfiles.path` repairs replaced
Kitty, Waybar, Rofi and Hyprland user-config symlinks. Vendor writes *through* a symlink
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
