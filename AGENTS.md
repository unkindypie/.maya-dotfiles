# Working in Maya dotfiles

These instructions apply throughout this repository.

## Purpose and ownership

Maintain a portable personal desktop: paper, warm white, muted pastels and soft
pink highlights, with Novel-inspired Kitty and tmux colors. Support both KooL
Fedora Hyprland and a fresh Hyprland installation without KooL. Preserve working
behavior and user customizations when changing appearance.

`home/` is the source of truth for installed files. Edit the repository first,
then apply the authorized changes to the live installation. Never rely on a
live-only edit: the restoration service can replace it. Keep README.md accurate
about installation, dependencies, behavior and limitations.

## Before changing anything

- Read README.md and the relevant installer, helper and configuration files.
- Check `git status` and preserve unrelated user edits. Work on `master` unless
  the user requests another branch. Never reset or rewrite history casually.
- Trace includes, imports, scripts, assets and command dependencies. Include or
  install everything necessary for the requested behavior on another machine.
- Use `$HOME`, `~`, XDG paths or paths derived from the checkout. Do not introduce
  `/home/may` or assume the repository can only live at its current location.

## Dependencies and installation

- Keep required dependencies available when applying changes. Inspect existing
  installations first; install missing dependencies through the existing
  installer rather than deleting, resetting or replacing working checkouts.
- Oh My Zsh, Zsh plugins and tmux plugins belong in dependencies.json with public
  URLs and exact commit hashes. Fetch them through scripts/install-dependencies.py.
  Do not vendor their upstream trees or use floating branch revisions.
- Preserve existing checkouts and local modifications. Changing a lock entry
  affects fresh installs; do not silently force an existing checkout to it.
- Keep custom themes, fonts, images and personal configuration in Git. Preserve
  original assets when making variants, and maintain ATTRIBUTION.md and licenses.
- Dependency downloads must be atomic, verify the requested revision, propagate
  failures and leave no partial destination. Do not fetch during shell startup.
- Keep installers idempotent and back up replaced files. Do not change the login
  shell, install system packages or modify unrelated settings without task scope.
- Preserve optional Maya Neovim installation, its explicit include/skip flags and
  noninteractive behavior. Apply personal mvim overrides after its installer.
  The mvim init is an override for Maya Neovim, not a standalone Neovim config.

## KooL and Hyprland compatibility

- Do not make active configs depend on KooL scripts, generated Wallust palettes,
  absolute vendor paths or imported KooL CSS. Keep reference/ as reference only.
- Preserve the restoration ownership model: maya-dotfiles.path restores owned
  Kitty/Waybar entry points and assets, and maya-waybar.service supervises the
  bar. Avoid duplicate watchers, restart loops and concurrent Waybar instances.
- Keep theme/wallpaper switches and whole-directory config replacements in mind.
  Do not promise update protection based only on a normal reload; test recovery.
- Avoid patching KooL's own scripts as the persistence mechanism. Keep protection
  in user-owned files/services outside the vendor-managed directories.
- Preserve tmux light/dark switching; style changes intended for light mode must
  not change dark mode. Keep shapes, spacing and text contrast consistent.
- Retain readable Kitty paper textures and their selected scale/tint. Consider
  default-background transparency when matching tmux text backgrounds and glyphs.
- Optional hardware and applications must fail gracefully. Document prerequisites
  and provide fallbacks where practical; do not claim support for untested setups.

## Secrets and machine-local state

- Never commit credentials, tokens, private keys, shell history, session history,
  logs or private machine-local overrides. Do not print secret values in tools.
- Track only the common `.zshrc`. Load secrets from ~/.config/zsh/secrets.zsh and
  non-secret machine overrides from ~/.config/zsh/local.zsh; keep both ignored.
- Preserve existing credential assignments during installation and keep private
  files and shell-config backups restricted to mode 600. Do not weaken checks
  or assume .gitignore alone makes copied files safe.
- Inspect staged changes and scan new personal files for accidentally copied
  secrets before committing. Never copy the raw live `.zshrc` into Git.

## Verification and delivery

Use checks appropriate to the change. For installer/dependency changes, run:

```sh
python3 tests/check.py
python3 tests/check-dependencies.py
```

Also check relevant Bash/Zsh/Lua syntax and `git diff --check`. For dependency
changes, verify new pins can be fetched into a temporary directory, preserving
local checkouts. Test fresh-home installation and repeated installation without
changing the real home just to exercise installer logic.

For live desktop changes, inspect service status and Waybar logs, verify Kitty
includes/assets resolve, and check tmux on an independent test server when
needed. Verify appearance visually when it matters. Test simulated vendor
replacement when changing protection behavior, and restore the intended state.
Do not run destructive desktop actions merely to test a menu entry.

Commit completed, verified repository changes on master as part of this dotfiles
workflow unless the user says otherwise. Stage relevant files, preserve unrelated
changes, and use a concrete commit message. Do not push or rewrite history unless
requested. Report the result, relevant checks, commit and material limitations
briefly; distinguish checks actually run from behavior inferred from code.
