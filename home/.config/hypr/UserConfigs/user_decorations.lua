local maya_colors = dofile((os.getenv("HOME") or "") .. "/.config/maya-theme/colors.lua")

-- Shared palette owns appearance; wallpaper tools do not supply UI colors.
-- Raised paper treatment, after wallpaper-derived colors.
hl.config({
  group = { col = { border_active = maya_colors.ansi_bright_white },
            groupbar = { col = { active = maya_colors.fallback_dark } } },
  general = {
    border_size = 3,
    col = {
      active_border = { colors = { maya_colors.rose, maya_colors.pink, maya_colors.lavender_border, maya_colors.rose }, angle = 45 },
      inactive_border = { colors = { maya_colors.sage_border, maya_colors.paper_inset, maya_colors.taupe }, angle = 135 },
    },
  },
  decoration = {
    active_opacity = 1.0,
    inactive_opacity = 1.0,
    fullscreen_opacity = 1.0,
    dim_inactive = false,
    dim_strength = 0.0,
    shadow = {
      enabled = true, range = 26, render_power = 2,
      color = maya_colors.focus_shadow, color_inactive = maya_colors.sheet_shadow, offset = "0 5",
    },
    blur = { enabled = true, size = 8, passes = 3, ignore_opacity = false },
  },
})

-- Kitty supplies an opaque surface; animate only compositor opacity.
hl.window_rule({
  match = { class = ".*" },
  opacity = "1.0 override 0.9 override 1.0 override",
})
hl.animation({ leaf = "fadeSwitch", enabled = true, speed = 6, bezier = "default" })
