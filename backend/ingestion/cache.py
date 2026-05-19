import json
from datetime import date
from pathlib import Path
from typing import Any

from backend.settings import settings


def cache_path(provider: str, suffix: str | None = None) -> Path:
    d = settings.cache_dir / provider
    d.mkdir(parents=True, exist_ok=True)
    name = f"{date.today().isoformat()}{f'_{suffix}' if suffix else ''}.json"
    return d / name


def write_cache(provider: str, data: Any, suffix: str | None = None) -> Path:
    path = cache_path(provider, suffix)
    path.write_text(json.dumps(data, default=str), encoding="utf-8")
    return path


def read_latest_cache(provider: str) -> Any | None:
    d = settings.cache_dir / provider
    if not d.exists():
        return None
    files = sorted(d.glob("*.json"), reverse=True)
    if not files:
        return None
    return json.loads(files[0].read_text(encoding="utf-8"))
