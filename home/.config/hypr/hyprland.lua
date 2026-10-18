-- Maya session. Load installed KooL modules when available, then personal overrides.
local base = (os.getenv("XDG_CONFIG_HOME") or (os.getenv("HOME") .. "/.config")) .. "/hypr/"
local function exists(path)
  local file = io.open(path, "r")
  if file then file:close(); return true end
  return false
end
local kool = exists(base .. "lua/settings.lua")
if kool then
  for _, name in ipairs({"env", "user_defaults", "settings", "decorations", "animations",
                         "window_rules", "layer_rules", "keybinds", "laptops", "monitors", "workspaces"}) do
    require(base .. "lua/" .. name .. ".lua")
  end
else
  -- Basic standalone desktop; personal bindings below extend these defaults.
  hl.monitor({ output = "", mode = "preferred", position = "auto", scale = "auto" })
  hl.bind("SUPER + Return", hl.dsp.exec_cmd("kitty"))
  hl.bind("SUPER + Q", hl.dsp.window.close())
  for n = 1, 9 do
    hl.bind("SUPER + " .. n, hl.dsp.focus({ workspace = n }))
    hl.bind("SUPER + SHIFT + " .. n, hl.dsp.window.move({ workspace = n }))
  end
end
for _, name in ipairs({"user_settings", "user_laptops", "user_window_rules", "user_keybinds", "user_decorations", "user_animations", "user_startup"}) do
  require(base .. "UserConfigs/" .. name .. ".lua")
end
