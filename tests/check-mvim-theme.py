#!/usr/bin/env python3
"""Check mvim variant selection and live updates without loading its separate repo."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
if not shutil.which('nvim'):
    raise SystemExit('Neovim is required for this integration check')

with tempfile.TemporaryDirectory(prefix='maya-mvim-theme-') as directory:
    home = Path(directory)
    palette = home / '.config/maya-theme'
    for mode in ('light', 'dark'):
        (palette / 'profiles' / mode).mkdir(parents=True)
    (palette / 'current').symlink_to(palette / 'profiles/light')
    script = home / 'check.lua'
    script.write_text('''local root = assert(vim.env.MAYA_TEST_ROOT)
package.path = root .. "/home/.config/mvim/lua/?.lua;" .. package.path
local theme = require("mvim.desktop_theme")
local config = dofile(root .. "/home/.config/mvim/init.lua")
assert(config.theme_background == "light")
package.loaded["maya.user"] = { config = config }
theme.setup()
assert(vim.o.background == "light")
local uv = vim.uv or vim.loop
local base = vim.env.XDG_CONFIG_HOME .. "/maya-theme/"
local function select(mode)
  assert(uv.fs_symlink(base .. "profiles/" .. mode, base .. "next"))
  assert(uv.fs_rename(base .. "next", base .. "current"))
  assert(vim.wait(2000, function() return vim.o.background == mode end, 10), "No live update to " .. mode)
  assert(config.theme_background == mode, "MayaConfig option was not synchronized")
end
select("dark")
theme.setup() -- Repeated setup must replace watchers, not duplicate them.
select("light")
assert(uv.fs_unlink(base .. "current"))
vim.api.nvim_exec_autocmds("FocusGained", {})
assert(theme.mode() == "light")
assert(config.theme_background == "light")
print("mvim config selection, live Light/Dark updates and Light fallback passed")
vim.cmd("qa!")
''')
    env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / '.config'), MAYA_TEST_ROOT=str(root))
    subprocess.run(['nvim', '--headless', '-u', 'NONE', '-l', str(script)], env=env, check=True, timeout=10)
