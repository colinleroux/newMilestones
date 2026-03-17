import json
from pathlib import Path

from flask import current_app, url_for

_manifest_cache = None
_manifest_mtime = None


def _manifest_path() -> Path:
    cfg_path = current_app.config.get('VITE_MANIFEST_PATH')
    if cfg_path:
        return Path(cfg_path)

    static_root = Path(current_app.static_folder) / 'vite'
    preferred = static_root / 'manifest.json'
    if preferred.exists():
        return preferred

    return static_root / '.vite' / 'manifest.json'


def _static_vite_base() -> str:
    base = current_app.config.get('VITE_STATIC_BASE', '/static/vite/')
    return base if base.endswith('/') else base + '/'


def _load_manifest() -> dict:
    global _manifest_cache, _manifest_mtime

    manifest_path = _manifest_path()
    if not manifest_path.exists():
        if current_app.debug:
            raise RuntimeError(f"Vite manifest not found at: {manifest_path}")
        return {}

    mtime = manifest_path.stat().st_mtime
    if _manifest_cache is None or _manifest_mtime != mtime:
        with manifest_path.open('r', encoding='utf-8') as manifest_file:
            _manifest_cache = json.load(manifest_file)
        _manifest_mtime = mtime

    return _manifest_cache


def _try_keys(manifest: dict, entry: str):
    if entry in manifest:
        return manifest[entry]

    candidates = []
    if entry.startswith('src/'):
        candidates += [entry[len('src/'):], f'./{entry}']
    else:
        candidates += [f'src/{entry}', f'./src/{entry}', f'./{entry}']
    candidates += [entry.lstrip('./'), entry.rstrip('/')]

    for candidate in candidates:
        if candidate in manifest:
            return manifest[candidate]

    for value in manifest.values():
        src = value.get('src')
        if src and (src.endswith(entry) or src.endswith('/' + entry.lstrip('/'))):
            return value

    return None


def asset_url(entry: str) -> str:
    manifest = _load_manifest()
    info = _try_keys(manifest, entry)
    if info and 'file' in info:
        return f"{_static_vite_base()}{info['file']}"
    return url_for('static', filename=f'vite/{entry}')


def asset_css_urls(entry: str):
    manifest = _load_manifest()
    info = _try_keys(manifest, entry) or {}
    return [f"{_static_vite_base()}{css_file.strip()}" for css_file in info.get('css', [])]
