"""Dependency security audit (replaces Sonatype + Aikido MCP for this repo)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_pip_audit() -> int:
    print("=== Python (pip-audit) ===")
    r = subprocess.run(
        [sys.executable, "-m", "pip_audit", "-f", "json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode not in (0, 1):
        print(r.stderr or r.stdout)
        return r.returncode
    try:
        data = json.loads(r.stdout or "[]")
    except json.JSONDecodeError:
        print(r.stdout)
        return r.returncode
    if not data:
        print("No known vulnerabilities in Python dependencies.")
        return 0
    found = False
    items = data if isinstance(data, list) else data.get("dependencies", [])
    for item in items:
        if isinstance(item, str):
            print(f"  {item}")
            found = True
            continue
        vulns = item.get("vulns") or []
        if vulns:
            found = True
            print(f"  {item.get('name')} {item.get('version')}: {len(vulns)} vuln(s)")
    if not found:
        print("No known vulnerabilities in Python dependencies.")
        return 0
    return 1


def run_npm_audit() -> int:
    print("\n=== Frontend (npm audit) ===")
    frontend = ROOT / "frontend"
    if not (frontend / "package-lock.json").exists() and not (frontend / "node_modules").exists():
        print("Skip: run npm install in frontend first")
        return 0
    r = subprocess.run(
        ["npm", "audit", "--json"],
        cwd=frontend,
        capture_output=True,
        text=True,
        shell=True,
    )
    try:
        data = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        print(r.stdout or r.stderr)
        return r.returncode
    vulns = data.get("metadata", {}).get("vulnerabilities", {})
    total = sum(vulns.values()) if isinstance(vulns, dict) else 0
    if total == 0:
        print("No vulnerabilities reported by npm audit.")
        return 0
    print(f"npm audit summary: {vulns}")
    return 1 if total else 0


def main() -> int:
    code = run_pip_audit()
    code = max(code, run_npm_audit())
    return code


if __name__ == "__main__":
    raise SystemExit(main())
