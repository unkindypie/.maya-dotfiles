-- Personal overrides. Restart mvim after editing this file.
-- Lua modules can live in lua/mvim/ and be loaded with require("mvim.name").
-- vim.g.everforest_background = "soft"
-- vim.opt.background = "light"

---@type MayaConfig
return {
	transparent_background = true,
	pokemon_sound_on_start_volume_percentage = 50, -- 0–100; 0 mutes playback.
	reopen_tabs = true, -- Restore saved files, tabs, and splits for this folder.
	pokemon_sound_on_start = true, -- Play the dashboard Pokémon cry.
	theme = "savq/melange-nvim",
	-- theme = "sainnhe/everforest",
	options = {
		background = "light",
		-- relativenumber = true,
		-- shiftwidth = 4,
	},
	plugins = {
		{
			"akinsho/bufferline.nvim",
			opts = {
				highlights = {
					fill = { bg = "#c4bea7" },
					background = { fg = "#514d43", bg = "#cec8b1" },
					buffer_visible = { fg = "#514d43", bg = "#d8d2bb", italic = false },
					buffer_selected = { fg = "#343e34", bg = "#f2efda", bold = true, italic = false },
					close_button = { fg = "#635e50", bg = "#cec8b1" },
					close_button_visible = { fg = "#635e50", bg = "#d8d2bb" },
					close_button_selected = { fg = "#343e34", bg = "#f2efda" },
					indicator_selected = { fg = "#526a36", bg = "#f2efda" },
					separator = { fg = "#c4bea7", bg = "#cec8b1" },
					separator_visible = { fg = "#c4bea7", bg = "#d8d2bb" },
					separator_selected = { fg = "#c4bea7", bg = "#f2efda" },
				},
			},
		},
		-- Extend or override an existing plugin's opts (lazy.nvim merges these).
		-- { "folke/which-key.nvim", opts = { delay = 200 } },
		-- Add plugins here, or import specs from lua/mvim/plugins/:
		-- { import = "mvim.plugins" },
	},
	setup = function()
		local function terminal_background()
			-- Keep hidden and ignored explorer entries readable on the light background.
			vim.api.nvim_set_hl(0, "SnacksPickerPathHidden", { fg = "#5c6a72" })
			vim.api.nvim_set_hl(0, "SnacksPickerPathIgnored", { fg = "#716b60", italic = true })
		end
		local group = vim.api.nvim_create_augroup("MvimTerminalBackground", { clear = true })
		vim.api.nvim_create_autocmd("ColorScheme", { group = group, callback = terminal_background })
		terminal_background()

		-- Runs after the built-in settings and keymaps.
		-- vim.keymap.set("n", "<leader>w", "<cmd>write<cr>", { desc = "My save" })
		-- vim.lsp.config("ty", { settings = { ty = {} } })
	end,
}
