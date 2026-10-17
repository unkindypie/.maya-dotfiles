"""Small backed-up compatibility fixes; do not vendor KooL source trees."""
from links import save_existing


def repair_dropdown(home, backup):
    script = home / '.config/hypr/scripts/Dropterminal.sh'
    if not script.is_file():
        return False
    original = script.read_text()
    # KooL's fallback takes ANY newly mapped window during concurrent startup.
    # Restrict its before/after comparison to the dropdown's dedicated class.
    updated = original.replace(
        "jq -r '.[].address'",
        "jq -r --arg CLASS \"$DROPDOWN_KITTY_CLASS\" "
        "'.[] | select(.class == $CLASS or .initialClass == $CLASS) | .address'",
    )
    if updated == original:
        return False
    save_existing(script, home, backup)
    script.write_text(updated)
    return True
