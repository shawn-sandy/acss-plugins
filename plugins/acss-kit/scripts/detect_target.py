#!/usr/bin/env python3
"""
Detect the target directory for fpkit-style React components.

Resolution:
  1. "generated" — <componentsDir>/ui.tsx exists locally.
  2. "none"      — neither.

componentsDir comes from .acss-target.json at project root, falling back to
"src/components/fpkit". The first invocation of /kit-add writes this file.

Usage:
    python detect_target.py [project_root]

Output (JSON to stdout):

    Generated path (preferred):
    {
      "source": "generated",
      "projectRoot": "/abs/path",
      "componentsDir": "src/components/fpkit",
      "importMapHint": "import Button from '../src/components/fpkit/button/button'"
    }

    No source found:
    {
      "source": "none",
      "projectRoot": null,
      "componentsDir": "src/components/fpkit",
      "importMapHint": "",
      "reasons": ["No project root containing react was found."]
    }

Exit code 0 = source detected (generated), 1 = none.
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

    if has_generated:
        result = {
            "source": "generated",
            "projectRoot": str(root),
            "componentsDir": components_dir,
            "importMapHint": f"import Button from '../{components_dir}/button/button'",
        }
        print(json.dumps(result, indent=2))
        return 0

    result = {
        "source": "none",
        "projectRoot": str(root),
        "componentsDir": components_dir,
        "importMapHint": "",
        "reasons": [
            "No fpkit component source found.",
            "Vendor components via /kit-add to bootstrap <componentsDir>/ui.tsx.",
        ],
    }
    print(json.dumps(result, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(main())
