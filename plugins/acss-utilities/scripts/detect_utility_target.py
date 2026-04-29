#!/usr/bin/env python3
"""
Detect the target directory for the acss-utilities CSS bundle.

Resolution:
  1. "configured" — `.acss-target.json` at project root has a
     `utilitiesDir` field pointing at an existing directory.
  2. "default"    — project root has react in dependencies, fall back
     to `src/styles/`.
  3. "none"       — no React project root in the path's ancestors.

Mirrors `acss-kit/scripts/detect_target.py`'s ancestor-walk and the
`.acss-target.json` schema. Adds an optional `utilitiesDir` field
without breaking existing acss-kit consumers.

Usage:
    python detect_utility_target.py [project_root]

Output (JSON to stdout):

    Configured path:
    {
      "source": "configured",
      "projectRoot": "/abs/path",
      "utilitiesDir": "src/styles",
      "bundlePath": "src/styles/utilities.css",
      "bridgePath": "src/styles/token-bridge.css",
      "reasons": []
    }

    Default path (react found, no .acss-target.json#utilitiesDir):
    {
      "source": "default",
      "projectRoot": "/abs/path",
      "utilitiesDir": "src/styles",
      "bundlePath": "src/styles/utilities.css",
      "bridgePath": "src/styles/token-bridge.css",
      "reasons": []
    }

    No project root found:
    {
      "source": "none",
      "projectRoot": null,
      "utilitiesDir": "src/styles",
      "bundlePath": "",
      "bridgePath": "",
      "reasons": ["No project root containing react was found."]
    }

Exit code 0 on success (configured or default), 1 on `none`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional


DEFAULT_UTILITIES_DIR = "src/styles"


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


def read_utilities_dir(root: Path) -> tuple[str, str]:
    """Return (utilities_dir, source) where source is 'configured' or 'default'.

    A configured `utilitiesDir` is only honored when `(root / utilitiesDir)`
    actually exists — otherwise the caller would select a non-existent path
    and `/utility-add` would fail later.
    """
    target = root / ".acss-target.json"
    if target.is_file():
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            cd = data.get("utilitiesDir")
            if isinstance(cd, str):
                configured = cd.strip()
                if configured and (root / configured).is_dir():
                    return configured, "configured"
        except Exception:
            pass
    return DEFAULT_UTILITIES_DIR, "default"


def main() -> int:
    start = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    root = find_project_root(start)
    if root is None:
        print(json.dumps({
            "source": "none",
            "projectRoot": None,
            "utilitiesDir": DEFAULT_UTILITIES_DIR,
            "bundlePath": "",
            "bridgePath": "",
            "reasons": ["No project root containing react was found."],
        }, indent=2))
        return 1

    utilities_dir, source = read_utilities_dir(root)
    bundle = f"{utilities_dir}/utilities.css"
    bridge = f"{utilities_dir}/token-bridge.css"

    print(json.dumps({
        "source": source,
        "projectRoot": str(root),
        "utilitiesDir": utilities_dir,
        "bundlePath": bundle,
        "bridgePath": bridge,
        "reasons": [],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
