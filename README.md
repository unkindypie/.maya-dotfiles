# Maya paper dotfiles

Personal paper / warm-white / pastel desktop with soft pink Waybar highlights.
No KooL dependency. This repository is the source of truth; edit files under
`home/`, then run `python3 install.py` to apply them.

## Install on a fresh Hyprland desktop

Clone this repository to `~/.maya-dotfiles` (another path also works), then:

```sh
cd ~/.maya-dotfiles
python3 install.py
# For the full Maya Neovim distribution and mvim launcher:
./bootstrap-mvim.sh
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
when the hardware is absent. Nerd Fonts are bundled. No sudo/package changes
are performed by install.py. Maya Neovim has its own dependency installer.

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
  sessionizer/session picker, and the installed plugins vendored with licenses.
  Plugin source revisions are recorded in dependencies.json. The theme works offline from the saved sources; tmux-thumbs may prompt to
  download or compile its platform-specific executable on first use. Git status has a bundled fallback if gitmux
  is absent. Prefix is Ctrl-b; r reloads; f opens the sessionizer.
- Exact personal `~/.config/mvim/init.lua` and lazy-lock.json. This is an override
  for Maya Neovim, not a standalone Neovim init; bootstrap-mvim.sh installs its
  upstream distribution. No private credentials or unrelated shell config.
- The regular, bold, italic and bold-italic faces of the installed Nerd Fonts.
- Original KooL Waybar config/modules/styles under reference/ for comparison;
  these are not installed and may refer to KooL-only programs.

The portable Waybar replaces KooL-only widgets (theme controls, updater, weather
wrapper, layout menus, Cava and hints) with independent core controls. It does
not install KooL or change Hyprland keybindings, monitors or wallpaper.
Obsidian-specific tmux popups require your Neovim Obsidian commands and notes;
those are personal workflow bindings, not supplied plugins.
Sessionizer project roots can be edited in home/scripts/tmux-sessionizer.

## Updates and ownership

`maya-dotfiles.path` watches Kitty/Waybar config replacements and runs
scripts/restore-managed.py. That restores owned entry points and Kitty assets
from this repository, including after directory replacement. The supervised
Waybar restarts if KooL kills it, and always loads the restored configuration.
This intentionally takes precedence over KooL's Kitty/Waybar theme pickers.
Edit the repo and reinstall rather than editing installed copies.
The previous kitty-notebook watcher is superseded and disabled.
The protection covers the inspected KooL update/theme behavior; deleting this
repository or disabling these services removes it. Other Waybar launchers can
create duplicate bars; disable those launchers on a new installation.

Disable protection with:

```sh
systemctl --user disable --now maya-dotfiles.path maya-waybar.service
```

Installer backups of replaced files live in ~/.local/state/maya-dotfiles/backups/.
No destructive cleanup is performed. tmux and mvim copies update on installation;
the continuous guard restores Kitty/Waybar only.

## Palette switches

Edit home/.tmux.theme.conf: `@theme_mode` is light or dark. Reinstall and Ctrl-b r.
Waybar is the paper palette regardless of desktop themes.
Edit home/.local/share/kitty-personal/notebook.conf for image/tint settings.

## Attribution

See ATTRIBUTION.md. Third-party files retain their original licenses.
