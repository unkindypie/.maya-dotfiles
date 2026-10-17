# Maya dotfiles

- Keep the paper/pastel style and support Hyprland with or without KooL.
- Read README.md and relevant files; preserve unrelated user changes.
- Configs in `home/` are linked into the live home: edits from either location
  must stay in sync. Keep Zsh secrets in local files, never in Git or tool output.
- Keep KooL link-recovery services working; avoid duplicate bars and restart loops.
  Symlinks cannot prevent vendor writes through them—document that limit.
- Install missing dependencies using pinned dependencies.json entries; preserve
  existing installations. Keep custom themes/assets, not upstream source trees.
- Use portable paths, back up replaced files, and keep installation repeatable.
- For installer changes run `python3 tests/check.py` and
  `python3 tests/check-dependencies.py`; check relevant syntax and `git diff --check`.
- Check live appearance/services when changed. Do not commit unless the user asks,
  or a critical/breaking change needs a recovery checkpoint. Otherwise leave edits
  uncommitted. Use `master`; never push or rewrite history unless requested.
- Use action-driven Conventional Commit subjects: `feat:`, `fix:`, `docs:`,
  `refactor:`, `style:` or `chore:` followed by a concise imperative description.
- Keep README.md accurate.

- Shared colors live in `color-palette/palette.json`. Run
  `python3 scripts/generate-palette.py`; do not hand-edit generated color files.
