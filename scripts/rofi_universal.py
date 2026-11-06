"""Optional rofi-universal v1.2.0 Fedora RPM installation."""
from pathlib import Path
import hashlib
import os
import platform
import shlex
import subprocess
import tempfile
import urllib.request

RELEASE_VERSION = '1.2.0'
RELEASE_BASE = (
    'https://github.com/Fl1pMoniz/rofi-universal/releases/download/v1.2.0'
)
MANIFEST_URL = f'{RELEASE_BASE}/SHA256SUMS'
PLUGIN_PATHS = (
    Path('/usr/lib64/rofi/libuniversal.so'),
    Path('/usr/lib/rofi/libuniversal.so'),
)
LAUNCHER = Path('/usr/bin/rofi-universal')
STATE_RELATIVE = Path('.local/state/maya-dotfiles/rofi-launcher')
PACKAGES = {
    'fedora42': {
        'os_version': '42',
        'rofi_version': '1.7.9',
        'rpm': 'rofi-universal-1.2.0-1.fc42.x86_64.rpm',
        'sha256': 'cfa260c641b60af40fb8b95c1e069e730f82965c6affd84e30f3e812200eaf4c',
    },
    'fedora44': {
        'os_version': '44',
        'rofi_version': '2.0.0',
        'rpm': 'rofi-universal-1.2.0-1.fc44.x86_64.rpm',
        'sha256': '952a81b4f3db5fb6d7fcc65f19637040fe42f93211d92e9cb0d0570c18fbc141',
    },
}


class RofiUniversalError(RuntimeError):
    pass


def os_release(path='/etc/os-release'):
    result = {}
    try:
        for line in Path(path).read_text().splitlines():
            key, separator, value = line.partition('=')
            if not separator or not key or key.startswith('#'):
                continue
            parsed = shlex.split(value)
            result[key] = parsed[0] if parsed else ''
    except OSError as error:
        raise RofiUniversalError(f'cannot read {path}: {error}') from error
    return result


def select_package(os_id, os_version, machine, rofi_version):
    """Return a package spec only for an explicitly compatible environment."""
    if machine not in ('x86_64', 'amd64'):
        raise RofiUniversalError(f'rofi-universal has no prebuilt package for {machine}')
    if os_id not in ('fedora', 'nobara'):
        raise RofiUniversalError(f'rofi-universal RPM is not supported on {os_id or "unknown"}')
    if os_version not in ('42', '44'):
        raise RofiUniversalError(f'rofi-universal RPM is not available for {os_id} {os_version}')
    package = PACKAGES[f'fedora{os_version}']
    if rofi_version != package['rofi_version']:
        raise RofiUniversalError(
            f'rofi-universal {RELEASE_VERSION} for Fedora {os_version} requires '
            f'Rofi {package["rofi_version"]}; installed: {rofi_version or "missing"}'
        )
    return package


def installed_rpm_version(package='rofi-universal'):
    try:
        result = subprocess.run(
            ['rpm', '-q', '--qf', '%{VERSION}', package],
            text=True, capture_output=True, check=False)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def rofi_version():
    try:
        result = subprocess.run(
            ['rpm', '-q', '--qf', '%{VERSION}', 'rofi'],
            text=True, capture_output=True, check=False)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def state_path(home):
    base = Path(os.environ.get('XDG_STATE_HOME', home / '.local/state'))
    return base / 'maya-dotfiles/rofi-launcher'


def write_launcher(home, universal):
    path = state_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.maya-rofi-state-', dir=path.parent) as tmp:
        temporary = Path(tmp) / 'state'
        temporary.write_text('universal\n' if universal else 'maya\n')
        os.replace(temporary, path)


def read_launcher(home):
    try:
        value = state_path(home).read_text().strip()
    except OSError:
        return 'maya'
    return value if value in ('maya', 'universal') else 'maya'


def _download(url, destination, timeout=30):
    request = urllib.request.Request(
        url, headers={'User-Agent': 'maya-dotfiles-rofi-universal'})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            destination.write_bytes(response.read(20 * 1024 * 1024 + 1))
    except OSError as error:
        raise RofiUniversalError(f'cannot download {url}: {error}') from error
    if destination.stat().st_size > 20 * 1024 * 1024:
        raise RofiUniversalError(f'downloaded file is unexpectedly large: {url}')


def _sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest(manifest_text, filename, expected_hash):
    entries = {}
    for line in manifest_text.splitlines():
        parts = line.split()
        if len(parts) == 2:
            entries[parts[1].lstrip('*')] = parts[0].lower()
    if entries.get(filename) != expected_hash:
        raise RofiUniversalError(
            f'SHA256SUMS does not contain the expected checksum for {filename}')
    return expected_hash


def verify_installed():
    if not any(path.is_file() for path in PLUGIN_PATHS) or not LAUNCHER.is_file():
        raise RofiUniversalError(
            'rofi-universal is installed but its plugin or launcher is missing; '
            'reinstall the package')
    version = installed_rpm_version()
    if version != RELEASE_VERSION:
        raise RofiUniversalError(
            f'rofi-universal {RELEASE_VERSION} was expected, found {version or "missing"}')


def install(home, skip_dependencies=False):
    release = os_release()
    os_id = release.get('ID', '').lower()
    os_version = release.get('VERSION_ID', '')
    package = select_package(
        os_id, os_version, platform.machine(), rofi_version())
    installed = installed_rpm_version()
    if installed == RELEASE_VERSION:
        verify_installed()
        return
    if installed:
        raise RofiUniversalError(
            f'rofi-universal {installed} is already installed; this installer '
            f'targets {RELEASE_VERSION}. Remove or update it explicitly.')
    if skip_dependencies:
        raise RofiUniversalError(
            'rofi-universal is not installed; rerun without '
            '--skip-dependencies or install the package manually')
    rpm_url = f'{RELEASE_BASE}/{package["rpm"]}'
    with tempfile.TemporaryDirectory(prefix='maya-rofi-universal-') as tmp:
        directory = Path(tmp)
        rpm = directory / package['rpm']
        manifest = directory / 'SHA256SUMS'
        _download(MANIFEST_URL, manifest)
        verify_manifest(manifest.read_text(), package['rpm'], package['sha256'])
        _download(rpm_url, rpm)
        actual = _sha256(rpm)
        if actual != package['sha256']:
            raise RofiUniversalError(
                f'checksum mismatch for {package["rpm"]}: {actual}')
        command = ['dnf', 'install', '-y', str(rpm)]
        if hasattr(os, 'geteuid') and os.geteuid() != 0:
            command.insert(0, 'sudo')
        try:
            subprocess.run(command, check=True)
        except (OSError, subprocess.CalledProcessError) as error:
            raise RofiUniversalError(f'package installation failed: {error}') from error
    verify_installed()
