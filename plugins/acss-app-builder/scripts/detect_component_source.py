#!/usr/bin/env python3
"""
Detect which fpkit component source to import from.

Resolution (first match wins):
  1. "generated" — <componentsDir>/ui.tsx exists locally.
  2. "npm"       — @fpkit/acss is in deps/devDeps and no generated source.
  3. "none"      — neither.

componentsDir comes from .acss-target.json at project root, falling back to
"src/components/fpkit".

Usage:
    python detect_component_source.py [project_root]

Output (JSON to stdout):
    {
      "source": "generated" | "npm" | "none",
      "projectRoot": "/abs/path",
      "componentsDir": "src/components/fpkit",
      "importMapHint": "...one example import line..."
    }

Exit code 0 = source detected, 1 = none.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional


DEFAULT_COMPONENTS_DIR = "src/components/fpkit"


def find_project_root(start: Path) -> Optional[Path]:
    cur = start.resolve()
    while True:
        pkg = cur / "package.json"
        if pkg.is_file():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "react" in deps:
                    return cur
            except Exception:
                pass
        if cur.parent == cur:
            return None
        cur = cur.parent


def read_components_dir(root: Path) -> str:
    target = root / ".acss-target.json"
    if target.is_file():
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            cd = data.get("componentsDir")
            if isinstance(cd, str) and cd.strip():
                return cd.strip()
        except Exception:
            pass
    return DEFAULT_COMPONENTS_DIR


def has_npm_fpkit(root: Path) -> bool:
    pkg = root / "package.json"
    if not pkg.is_file():
        return False
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        return "@fpkit/acss" in deps
    except Exception:
        return False


def main() -> int:
    start = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    root = find_project_root(start)
    if root is None:
        print(json.dumps({
            "source": "none",
            "projectRoot": None,
            "componentsDir": DEFAULT_COMPONENTS_DIR,
            "importMapHint": "",
            "reasons": ["No project root containing react was found."],
        }))
        return 1

    components_dir = read_components_dir(root)
    has_generated = (root / components_dir / "ui.tsx").is_file()
    has_npm = has_npm_fpkit(root)

    if has_generated:
        source = "generated"
        hint = f"import Button from '../{components_dir}/button/button'"
    elif has_npm:
        source = "npm"
        hint = "import { Button } from '@fpkit/acss'"
    else:
        source = "none"
        hint = ""

    print(json.dumps({
        "source": source,
        "projectRoot": str(root),
        "componentsDir": components_dir,
        "importMapHint": hint,
    }, indent=2))
    return 0 if source != "none" else 1


if __name__ == "__main__":
    sys.exit(main())
