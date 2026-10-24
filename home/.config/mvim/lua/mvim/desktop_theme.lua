-- Select mvim's own theme variant from the global Maya mode; do not supply colors.
local M = {}
local uv = vim.uv or vim.loop
local watcher

local function directory()
  local config = vim.env.XDG_CONFIG_HOME
  if not config or config == "" then
    config = vim.fn.expand("~/.config")
  end
  return config .. "/maya-theme"
end

function M.mode()
  local target = uv.fs_readlink(directory() .. "/current") or ""
  local selected = target:match("([^/]+)/*$")
  return selected == "dark" and "dark" or "light"
end

function M.apply()
  local selected = M.mode()
  -- Keep the new MayaConfig option in sync, including later theme/plugin reloads.
  local user = package.loaded["maya.user"]
  if user and type(user.config) == "table" then
    user.config.theme_background = selected
  end
  if vim.o.background ~= selected then
    -- Neovim reloads the current colorscheme when 'background' changes.
    vim.o.background = selected
  end
end

local function stop()
  if watcher then
    watcher:stop()
    if not watcher:is_closing() then
      watcher:close()
    end
    watcher = nil
  end
end

local function watch()
  if watcher or not uv.fs_stat(directory()) then
    return
  end
  watcher = uv.new_fs_event()
  if not watcher then
    return
  end
  local started = watcher:start(directory(), {}, vim.schedule_wrap(function(err, name)
    if not err and (name == nil or name == "current") then
      M.apply()
    end
  end))
  if not started then
    stop()
  end
end

function M.setup()
  stop()
  local group = vim.api.nvim_create_augroup("MvimDesktopTheme", { clear = true })
  vim.api.nvim_create_autocmd("FocusGained", {
    group = group,
    callback = function()
      watch() -- Recover if the palette directory was installed after mvim started.
      M.apply()
    end,
  })
  vim.api.nvim_create_autocmd("VimLeavePre", { group = group, callback = stop })
  watch()
  M.apply()
end

return M
