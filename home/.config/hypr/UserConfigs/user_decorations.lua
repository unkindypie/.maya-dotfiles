local maya_colors = dofile((os.getenv("HOME") or "") .. "/.config/maya-theme/colors.lua")

-- ==================================================
--  KoolDots (2026)
--  Project URL: https://github.com/LinuxBeginnings
--  License: GNU GPLv3
--  SPDX-License-Identifier: GPL-3.0-or-later
-- ==================================================

-- User decorations overrides (auto-generated).
-- This file is intentionally split from other user overrides.
-- Add only user-specific Lua overrides here.
-- Example:
-- hl.config({ general = { gaps_in = 4, gaps_out = 8 } })

-- Source reference from UserDecorations.conf (hyprlang):
-- source = $HOME/.config/hypr/wallust/wallust-hyprland.conf
-- general {
-- border_size = 3
-- gaps_in = 2
-- gaps_out = 4
-- col.active_border = $color12
-- col.inactive_border = $color10
-- }
-- decoration {
-- rounding = 10
-- active_opacity = 1.0
-- inactive_opacity = 0.9
-- fullscreen_opacity = 1.0
-- dim_inactive = false
-- dim_strength = 0.1
-- dim_special = 0.8
-- shadow {
-- enabled = true
-- range = 3
-- render_power = 1
-- color =  $color12
-- color_inactive = $color10
-- }
-- blur {
-- enabled = true
-- size = 6
-- passes = 3
-- new_optimizations = true
-- xray = true
-- ignore_opacity = true
-- special = true
-- popups = true
-- }
-- }
-- group {
-- col.border_active = $color15
-- groupbar {
-- col.active = $color0
-- }
-- }

local function read_wallust_colors(path)
  local colors = {}
  local handle = io.open(path, "r")
  if not handle then
    return colors
  end
  for line in handle:lines() do
    local key, hex = line:match("^%$([%w_]+)%s*=%s*rgb%(([0-9A-Fa-f]+)%)")
    if key and hex then
      colors[key] = "rgb(" .. hex .. ")"
    end
  end
  handle:close()
  return colors
end

local wallust_path = (os.getenv("HOME") or "") .. "/.config/hypr/wallust/wallust-hyprland.conf"
local colors = read_wallust_colors(wallust_path)

if next(colors) then
  hl.config({
    general = {
      col = {
        active_border = colors.color12 or maya_colors.fallback_blue,
        inactive_border = colors.color10 or maya_colors.fallback_gray,
      },
    },
  })

  hl.config({
    decoration = {
      shadow = {
        color = colors.color12 or maya_colors.fallback_blue,
        color_inactive = colors.color10 or maya_colors.fallback_gray,
      },
    },
  })

  hl.config({
    group = {
      col = {
        border_active = colors.color15 or maya_colors.ansi_bright_white,
      },
      groupbar = {
        col = {
          active = colors.color0 or maya_colors.fallback_dark,
        },
      },
    },
  })
end

-- Raised paper treatment, after wallpaper-derived colors.
hl.config({
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

-- Animate compositor opacity; only focused windows ignore app alpha.
hl.window_rule({
  match = { class = ".*" },
  opacity = "1.0 override 0.9 override 1.0 override",
})
hl.window_rule({ match = { focus = true }, force_rgbx = true })
hl.animation({ leaf = "fadeSwitch", enabled = true, speed = 6, bezier = "default" })
