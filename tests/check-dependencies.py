#!/usr/bin/env python3
"""Verify pinned installation, preservation, and failed-fetch cleanup using local Git."""
from pathlib import Path
import runpy, subprocess, tempfile
root = Path(__file__).resolve().parents[1]
install_one = runpy.run_path(str(root / 'scripts/install-dependencies.py'))['install_one']
with tempfile.TemporaryDirectory() as d:
    base = Path(d); source = base / 'source'; target = base / 'target'
    subprocess.run(['git', 'init', '-q', str(source)], check=True)
    (source / 'value').write_text('pinned content')
    subprocess.run(['git', '-C', str(source), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(source), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture'], check=True)
    revision = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    spec = {'url': source.as_uri(), 'commit': revision}
    install_one(spec, target)
    assert (target / 'value').read_text() == 'pinned content'
    (target / 'value').write_text('local change')
    install_one(spec, target)
    assert (target / 'value').read_text() == 'local change'
    broken = base / 'failed'
    try:
        install_one({'url': (base / 'nonexistent').as_uri(), 'commit': revision}, broken)
    except subprocess.CalledProcessError:
        pass
    else:
        raise AssertionError('Failed download did not propagate')
    assert not broken.exists()
    assert not list(base.glob('.maya-dependency-*'))
print('Pinned install, local-change preservation and failure cleanup passed')
