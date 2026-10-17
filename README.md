# Maya paper dotfiles

Personal paper / warm-white / pastel desktop with soft pink Waybar highlights.
No KooL dependency. This repository is the source of truth; edit files under
`home/`, or edit the installed symlinks directly: both edit the same files.
Rerun `python3 install.py` when adding new files. Reload applications as needed.

## Install on a fresh Hyprland desktop

Clone this repository to `~/.maya-dotfiles` (another path also works), then:

```sh
cd ~/.maya-dotfiles
python3 install.py  # asks whether to install Maya Neovim (default: no)
# Explicit choices, including unattended installs:
python3 install.py --with-mvim
python3 install.py --without-mvim
```

Install prerequisites first. Fedora example (package names may vary by release):

```sh
sudo dnf install waybar kitty tmux python3 git fzf wl-clipboard \
  rofi-wayland brightnessctl wireplumber pulseaudio-utils pavucontrol \
  NetworkManager-tui playerctl fontconfig
```

Use a running Hyprland session with a systemd user manager. PipeWire's PulseAudio
compatibility service supplies Waybar audio. SwayNC and hyprlock are optional;
notifications hide if SwayNC is absent. The lock action falls back to loginctl,
which requires your session's lock handler. Backlight and battery modules hide
when the hardware is absent. Nerd Fonts are bundled. The dotfiles installation itself does not change system packages. Choosing
`--with-mvim` invokes Maya Neovim's dependency installer, which may request sudo
or further choices. Non-interactive runs skip Maya Neovim unless `--with-mvim`
is supplied. Existing Maya Neovim checkouts are reused; fresh clones use the
revision in dependencies.json. Personal overrides are applied afterward.

The enabled `maya-waybar.service` starts/restarts the bar independently of KooL.
On a non-systemd installation use `python3 install.py --no-services` and add
`exec-once = ~/.local/bin/maya-waybar` to your Hyprland configuration instead;
automatic restoration requires systemd. The launcher can discover the Wayland
socket if your session has not imported WAYLAND_DISPLAY into systemd.

## Included

- Self-contained Waybar layout, CSS and action script: workspaces, title, app
  launcher, clock/calendar, media, CPU/memory, network, brightness, battery,
  audio/microphone, idle inhibitor, optional notifications, tray and session menu.
- Kitty config, complete installed theme collection, Novel palette, original
  Notebook/Lined Paper assets, generated alternative, and 110%/121% tiles.
  Current choice is Lined Paper at 121%, tint 0.35.
- tmux config, reset bindings, light/dark variable, Python palette helper,
  sessionizer/session picker, and a pinned installer for tmux plugins.
  Plugin URLs and revisions are recorded in dependencies.json; tmux-thumbs may prompt to
  download or compile its platform-specific executable on first use. Git status has a bundled fallback if gitmux
  is absent. Prefix is Ctrl-b; r reloads; f opens the sessionizer.
- Exact personal `~/.config/mvim/init.lua` and lazy-lock.json. This is an override
  for Maya Neovim, not a standalone Neovim init; bootstrap-mvim.sh installs its
  upstream distribution. No private credentials.
- The regular, bold, italic and bold-italic faces of the installed Nerd Fonts.
- Original KooL Waybar config/modules/styles under reference/ for comparison;
  these are not installed and may refer to KooL-only programs.

The portable Waybar replaces KooL-only widgets (theme controls, updater, weather
wrapper, layout menus, Cava and hints) with independent core controls. It does
not install KooL or change Hyprland keybindings, monitors or wallpaper.
Obsidian-specific tmux popups require your Neovim Obsidian commands and notes;
those are personal workflow bindings, not supplied plugins.
Sessionizer project roots can be edited in home/scripts/tmux-sessionizer.

## Dependency installation

The normal installer downloads missing Oh My Zsh, Zsh plugins, TPM and tmux
plugins at the exact commits in dependencies.json. Git and internet are needed
for a fresh setup. Each download is verified and installed atomically; failures
leave no partial installation. Existing directories are preserved without fetch,
checkout, reset or upgrade, including local edits and different revisions.
The pins therefore specify fresh installs, not forced upgrades.

Run `python3 scripts/install-dependencies.py` to install dependencies alone.
Use `python3 install.py --skip-dependencies --without-mvim` for an offline,
config-only installation when dependencies are already available. A custom theme
directory alone is not a full Oh My Zsh installation; remove or move that partial
directory before doing a fresh dependency install. Do not use config-only mode
as the first step of a new installation.

Upstream source trees are not tracked in the current checkout. Fonts, images,
custom themes and personal configuration remain in Git. Previous commits still
contain the old snapshots; history has not been rewritten.

## Zsh

The linked `~/.config/zsh/shared.zsh` includes your current tonotdo theme, remembered theme choices,
plugins, aliases, history, guarded optional tools, and automatic interactive tmux.
Oh My Zsh, autosuggestions and syntax highlighting are installed from the pinned
Git URLs/revisions in dependencies.json. Sobole and the local agnosterzak theme
remain bundled. Install `zsh` and optionally `lsd` / `fastfetch`.
The installer does not change your login shell; use `chsh -s "$(command -v zsh)"`
if desired. The Pokémon Fastfetch integration activates only when its optional
external config exists.

`~/.zshrc` is a small local loader, not a link into Git. Put shared shell edits
in `~/.config/zsh/shared.zsh` (linked to the repo). Loader edits remain local.
Keep credentials in `~/.config/zsh/secrets.zsh` (chmod 600), and machine-specific
non-secret overrides in `~/.config/zsh/local.zsh`. Both are sourced but excluded
from Git. The installer preserves recognized single-line credential assignments
from an existing `.zshrc` in the private file before replacing it; multiline
credentials must be moved manually. Backups of `.zshrc` get mode 600.
Review any other private settings before migrating a different machine.

## Updates and ownership

`maya-dotfiles.path` watches Kitty/Waybar config replacements and runs
scripts/restore-managed.py. That restores symlinks for owned entry points and Kitty assets
from this repository, including after directory replacement. The supervised
Waybar restarts if KooL kills it, and always loads the restored configuration.
This intentionally takes precedence over KooL's Kitty/Waybar theme pickers.
Editing a correctly linked config updates the repo immediately. Recovery does
not reset those edits. Replaced files are backed up before relinking. Symlinks
cannot protect against vendor writes through the link: such writes also modify
the repo. Review `git diff` after using vendor theme tools; Git provides recovery
for committed versions. Do not treat this as protection against every vendor write.
The previous kitty-notebook watcher is superseded and disabled.
The protection covers the inspected KooL update/theme behavior; deleting this
repository or disabling these services removes it. Other Waybar launchers can
create duplicate bars; disable those launchers on a new installation.

Disable protection with:

```sh
systemctl --user disable --now maya-dotfiles.path maya-waybar.service
```

Installer backups of replaced files live in ~/.local/state/maya-dotfiles/backups/.
All tracked files under home/ are installed as individual symlinks, including
tmux, mvim, helpers, fonts and assets. Private files stay local. The continuous
guard repairs Kitty/Waybar links only. Existing differing configs are backed up
before initial linking; review backups for any local changes you want to retain.

## Palette switches

Edit home/.tmux.theme.conf: `@theme_mode` is light or dark. Press Ctrl-b r to reload.
Waybar is the paper palette regardless of desktop themes.
Edit home/.local/share/kitty-personal/notebook.conf for image/tint settings.

## Attribution

See ATTRIBUTION.md. Third-party files retain their original licenses.
