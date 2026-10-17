#!/usr/bin/env python3
"""Apply the personal Novel-inspired light palette after loading Mocha."""
import subprocess

def get(name):
    return subprocess.check_output(["tmux", "show-option", "-gqv", name], text=True).rstrip("\n")

if get("@theme_mode") == "light":
    background = get("@theme_light_background")
    subprocess.run(["tmux", "set-option", "-g", "status-bg", background], check=True)
    for option in ("status-left", "status-right", "window-status-format", "window-status-current-format"):
        value = get(option).replace("bg=#1e1e2e", "bg=" + background)
        # The active tab starts with an empty rounded edge in the bar color.
        value = value.replace("fg=#1e1e2e,bg=" + background,
                              "fg=" + background + ",bg=" + background)
        if option in ("status-left", "status-right"):
            # Warm paper segments, taupe icons, peach while prefix is held.
            value = value.replace("#313244", "#c8c2ac")
            value = value.replace("#cdd6f4", "#3b2322")
            value = value.replace("#1e1e2e", "#3b2322")
            value = value.replace("#a6e3a1", "#b5aa96")
            value = value.replace("#f38ba8", "#fab387")
            value = value.replace("#cba6f7", "#b5aa96")
        if option == "window-status-format":
            # Muted paper labels and taupe numbers, with Novel brown text.
            fill = "#c8c2ac"
            text = "#3b2322"
            accent = "#b5aa96"
            value = (
                f"#[fg={fill},bg={background},nobold,nounderscore,noitalics]"
                f"#[fg={text},bg={fill}]#W "
                f"#[fg={text},bg={accent},nobold,nounderscore,noitalics] #I"
                f"#[fg={accent},bg={background}] "
            )
        if option == "window-status-current-format":
            # Match the normal rounded tab with one consistent light fill.
            # Avoid Kitty applying default-background transparency to the label.
            fill = "#dedac2"
            text = "#3b2322"
            accent = "#fab387"
            value = (
                f"#[fg={fill},bg={background},nobold,nounderscore,noitalics]"
                f"#[fg={text},bg={fill}]#W#{{?window_zoomed_flag,(),}} "
                f"#[fg={text},bg={accent},nobold,nounderscore,noitalics] #I"
                f"#[fg={accent},bg={background}] "
            )
        subprocess.run(["tmux", "set-option", "-g", option, value], check=True)

# Keep the rounded bar compact: tmux cannot add pixel-sized vertical padding.
base_format = get('@maya_original_status_format')
if not base_format:
    base_format = get('status-format[0]')
    subprocess.run(['tmux', 'set-option', '-g', '@maya_original_status_format', base_format], check=True)
if get('@theme_mode') == 'light':
    outer = '#dfdbc3'  # Novel paper outside the rounded status background.
    for option, edge in [('status-left', ''), ('status-right', '')]:
        value = get(option)
        cap = f'#[fg={background},bg={outer}]{edge}#[bg={background}]'
        value = cap + value if option == 'status-left' else value + cap
        subprocess.run(['tmux', 'set-option', '-g', option, value], check=True)
    subprocess.run(['tmux', 'set-option', '-g', 'status', 'on'], check=True)
    subprocess.run(['tmux', 'set-option', '-g', 'status-format[0]', base_format], check=True)
else:
    subprocess.run(['tmux', 'set-option', '-g', 'status', 'on'], check=True)
    subprocess.run(['tmux', 'set-option', '-g', 'status-format[0]', base_format], check=True)
