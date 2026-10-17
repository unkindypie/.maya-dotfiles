#!/usr/bin/env python3
"""Check dropdown filtering, backups, and repeatable repair."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from kool import repair_dropdown

with tempfile.TemporaryDirectory() as directory:
    home = Path(directory)
    backup = home / 'backup'
    assert not repair_dropdown(home, backup)
    script = home / '.config/hypr/scripts/Dropterminal.sh'
    script.parent.mkdir(parents=True)
    original = "jq -r '.[].address'"
    script.write_text(original)
    assert repair_dropdown(home, backup)
    assert (backup / script.relative_to(home)).read_text() == original
    assert not repair_dropdown(home, backup)
    clients = [dict(address='ordinary', **{'class': 'kitty', 'initialClass': 'kitty'}),
               dict(address='dropdown', **{'class': 'kitty-dropterm', 'initialClass': 'kitty-dropterm'})]
    result = subprocess.run(['bash', '-c', 'DROPDOWN_KITTY_CLASS=kitty-dropterm; ' + script.read_text()],
                            input=json.dumps(clients), text=True, capture_output=True, check=True)
    assert result.stdout.strip() == 'dropdown'
print('Dropdown filtering, backup, and repeatability checks passed')
