#!/usr/bin/env python3
"""Check optional rofi-universal platform selection and launcher wrapper."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'scripts'))
import rofi_universal as ru

assert ru.select_package('fedora', '42', 'x86_64', '1.7.9')['rpm'].endswith('fc42.x86_64.rpm')
assert ru.select_package('fedora', '44', 'x86_64', '2.0.0')['rpm'].endswith('fc44.x86_64.rpm')
assert ru.select_package('nobara', '44', 'x86_64', '2.0.0')['rpm'].endswith('fc44.x86_64.rpm')
for args in [
    ('fedora', '42', 'x86_64', '2.0.0'),
    ('fedora', '44', 'x86_64', '1.7.9'),
    ('fedora', '43', 'x86_64', '2.0.0'),
    ('nobara', '43', 'x86_64', '2.0.0'),
    ('fedora', '44', 'aarch64', '2.0.0'),
    ('arch', '44', 'x86_64', '2.0.0'),
    ('fedora', '44', 'x86_64', ''),
]:
    try:
        ru.select_package(*args)
    except ru.RofiUniversalError:
        pass
    else:
        raise AssertionError(f'unexpected compatible platform: {args!r}')

manifest = (
    'cfa260c641b60af40fb8b95c1e069e730f82965c6affd84e30f3e812200eaf4c  '
    'rofi-universal-1.2.0-1.fc42.x86_64.rpm\n')
assert ru.verify_manifest(
    manifest, 'rofi-universal-1.2.0-1.fc42.x86_64.rpm',
    'cfa260c641b60af40fb8b95c1e069e730f82965c6affd84e30f3e812200eaf4c')
try:
    ru.verify_manifest(manifest, 'rofi-universal-1.2.0-1.fc42.x86_64.rpm', '0' * 64)
except ru.RofiUniversalError:
    pass
else:
    raise AssertionError('bad checksum was accepted')

with tempfile.TemporaryDirectory(prefix='maya-rofi-wrapper-') as tmp:
    home = Path(tmp)
    os.environ['XDG_STATE_HOME'] = str(home / '.local/state')
    bindir = home / 'bin'
    bindir.mkdir()
    log = home / 'launch.log'

    def executable(name, body):
        path = bindir / name
        path.write_text('#!/bin/sh\n' + body)
        path.chmod(0o755)

    executable('rofi', f'printf "%s\\n" "$@" > {log}\n')
    executable('rofi-universal', f'printf "universal:%s\\n" "$@" >> {log}\n')
    env = dict(os.environ, HOME=str(home),
               PATH=f'{bindir}:/usr/bin:/bin')
    wrapper = root / 'home/.local/bin/maya-rofi'

    def run_wrapper():
        log.unlink(missing_ok=True)
        subprocess.run(['sh', str(wrapper)], env=env, check=True, timeout=5)
        return log.read_text()

    assert 'maya' == ru.read_launcher(home)
    output = run_wrapper()
    assert '-show\ndrun' in output

    ru.write_launcher(home, True)
    assert ru.read_launcher(home) == 'universal'
    output = run_wrapper()
    assert output.startswith('universal:')

    # Missing universal executable must fail visibly, not silently launch Maya.
    (bindir / 'rofi-universal').unlink()
    log.unlink(missing_ok=True)
    failure = subprocess.run(['sh', str(wrapper)], env=env, text=True,
                             capture_output=True, timeout=5)
    assert failure.returncode != 0
    assert '-e' in log.read_text()

print('rofi-universal platform, checksum and launcher checks passed')
