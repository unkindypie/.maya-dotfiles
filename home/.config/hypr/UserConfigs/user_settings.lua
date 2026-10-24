-- Personal keyboard, monitor and layout settings.
hl.env("LIBVA_DRIVER_NAME", "radeonsi")
-- Let qt5ct/qt6ct apply the generated Maya palette instead of KooL's Kvantum override.
hl.env("QT_STYLE_OVERRIDE", "")
-- qt6ct also advertises the qt5ct key, so both Qt versions can use this value.
hl.env("QT_QPA_PLATFORMTHEME", "qt5ct")
hl.config({
  input = { kb_layout = "us,ua", kb_options = "" },
  general = { gaps_in = 4, gaps_out = 6 },
  cursor = { no_hardware_cursors = 1 },
})
require((os.getenv("XDG_CONFIG_HOME") or (os.getenv("HOME") .. "/.config")) .. "/hypr/UserConfigs/monitors.lua")

-- Preserve the extra touchpad gestures omitted by KooL's Lua defaults.
for direction, factor in pairs({ up = 1.5, down = 1 / 1.5 }) do
  hl.gesture({ fingers = 3, direction = direction, action = function()
    local current = hl.get_config("cursor:zoom_factor")
    hl.config({ cursor = { zoom_factor = math.max(1, current) * factor } })
  end })
end
hl.gesture({ fingers = 4, direction = "up", action = function()
  hl.exec_cmd('"$HOME/.config/hypr/scripts/OverviewToggle.sh"')
end })
hl.gesture({ fingers = 4, direction = "down", action = "float" })
