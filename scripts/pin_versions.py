"""Print pinned dependency versions (replaces Sonatype version recommendations)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def python_pins() -> dict[str, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    pins = {}
    for line in r.stdout.splitlines():
        if "==" in line and not line.startswith("-"):
            name, ver = line.split("==", 1)
            pins[name.lower()] = ver
    return pins


def npm_pins() -> dict[str, str]:
    pkg = ROOT / "frontend" / "package.json"
    if not pkg.exists():
        return {}
    data = json.loads(pkg.read_text(encoding="utf-8"))
    out = {}
    for section in ("dependencies", "devDependencies"):
        for name, ver in (data.get(section) or {}).items():
            out[name] = ver
    return out


def main() -> None:
    print("=== Installed Python packages (pip freeze) ===")
    for name in sorted(python_pins()):
        if name in ("fastapi", "duckdb", "uvicorn", "httpx", "numpy", "simpy", "pydantic"):
            print(f"  {name}=={python_pins()[name]}")
    print("\n=== Frontend package.json ranges ===")
    for name, ver in sorted(npm_pins().items()):
        print(f"  {name}: {ver}")
    print("\nRun 'make audit-all' for vulnerability scan (no Sonatype MCP required).")


if __name__ == "__main__":
    main()
