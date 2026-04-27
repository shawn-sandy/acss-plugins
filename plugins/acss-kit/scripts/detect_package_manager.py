#!/usr/bin/env python3
"""
Detect the package manager for a JavaScript project.

Inspection priority (first match wins, walking from package root upward):
  1. pnpm-lock.yaml          → pnpm
  2. yarn.lock               → yarn
  3. bun.lock (text, 1.2+)   → bun
  4. bun.lockb (binary)      → bun
  5. package-lock.json       → npm
  6. package.json#packageManager field (name@version spec, walks ancestors)
  7. npm (final fallback)

Lockfile search walks ancestor directories so monorepo/workspace setups
are handled correctly — workspace lockfiles live at the workspace root,
not inside each package.

Usage:
    python detect_package_manager.py [project_root]
    python detect_package_manager.py --self-test

Output (JSON to stdout):

    Success:
    {
      "manager": "pnpm",
      "lockfile": "pnpm-lock.yaml",
      "installCommand": "pnpm add -D",
      "projectRoot": "/abs/path",
      "reasons": []
    }

    Failure (no project root found):
    {
      "manager": null,
      "lockfile": null,
      "installCommand": null,
      "projectRoot": null,
      "reasons": ["No package.json found in any ancestor directory."]
    }

Exit code 0 = manager detected, 1 = no project root found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional

LOCKFILE_PRIORITY = [
    ("pnpm-lock.yaml", "pnpm"),
    ("yarn.lock", "yarn"),
    ("bun.lock", "bun"),
    ("bun.lockb", "bun"),
    ("package-lock.json", "npm"),
]

INSTALL_COMMANDS = {
    "npm": "npm install -D",
    "pnpm": "pnpm add -D",
    "yarn": "yarn add -D",
    "bun": "bun add -d",
}


def find_project_root(start: Path) -> Optional[Path]:
    """Walk from start upward; return first directory containing package.json."""
    cur = start.resolve()
    while True:
        if (cur / "package.json").is_file():
            return cur
        if cur.parent == cur:
            return None
        cur = cur.parent


def find_lockfile(start: Path) -> tuple[Optional[str], Optional[str]]:
    """Walk from start upward; return (filename, manager) for first lockfile found.

    Walks ancestors so monorepo workspace lockfiles (at the workspace root)
    are found even when start is a nested package directory.
    """
    cur = start.resolve()
    while True:
        for filename, pm in LOCKFILE_PRIORITY:
            if (cur / filename).is_file():
                return filename, pm
        if cur.parent == cur:
            return None, None
        cur = cur.parent


def find_packagemanager_field(start: Path) -> Optional[str]:
    """Walk from start upward; return manager from first packageManager field found.

    Handles workspace roots that carry the packageManager field on the root
    package.json rather than on nested package package.json files.
    """
    cur = start.resolve()
    while True:
        pkg_path = cur / "package.json"
        if pkg_path.is_file():
            try:
                pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
                pm_field = pkg.get("packageManager", "")
                if pm_field:
                    m = re.match(r"^([a-z]+)@", pm_field)
                    if m and m.group(1) in INSTALL_COMMANDS:
                        return m.group(1)
            except Exception:
                pass
        if cur.parent == cur:
            return None
        cur = cur.parent


def detect_manager(root: Path) -> dict:
    lockfile_name, manager = find_lockfile(root)

    if lockfile_name is None:
        manager = find_packagemanager_field(root) or "npm"

    return {
        "manager": manager,
        "lockfile": lockfile_name,
        "installCommand": INSTALL_COMMANDS[manager],
        "projectRoot": str(root),
        "reasons": [],
    }


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        return self_test()

    start = Path(args[0]).resolve() if args else Path.cwd()
    root = find_project_root(start)
    if root is None:
        print(json.dumps({
            "manager": None,
            "lockfile": None,
            "installCommand": None,
            "projectRoot": None,
            "reasons": ["No package.json found in any ancestor directory."],
        }))
        return 1

    print(json.dumps(detect_manager(root)))
    return 0


def self_test() -> int:
    import tempfile

    passed = 0
    failed = 0

    def run(
        name: str,
        files: dict,
        expected_manager: str,
        expected_lockfile: Optional[str] = None,
    ) -> None:
        nonlocal passed, failed
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for filename, content in files.items():
                (root / filename).write_text(content, encoding="utf-8")
            result = detect_manager(root)
            manager_ok = result["manager"] == expected_manager
            lockfile_ok = expected_lockfile is None or result["lockfile"] == expected_lockfile
            if manager_ok and lockfile_ok:
                print(f"PASS: {name}")
                passed += 1
            else:
                detail = f"manager={result['manager']!r}, lockfile={result['lockfile']!r}"
                print(f"FAIL: {name} — got {detail}")
                failed += 1

    run(
        "pnpm-lock.yaml → pnpm",
        {"package.json": '{"name":"test"}', "pnpm-lock.yaml": ""},
        "pnpm",
        "pnpm-lock.yaml",
    )
    run(
        "package-lock.json → npm",
        {"package.json": '{"name":"test"}', "package-lock.json": "{}"},
        "npm",
        "package-lock.json",
    )
    run(
        "packageManager field → yarn (no lockfile)",
        {"package.json": '{"name":"test","packageManager":"yarn@3.6.0"}'},
        "yarn",
        None,
    )

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED")
        return 1
    print(f"\nAll {total} self-tests PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
