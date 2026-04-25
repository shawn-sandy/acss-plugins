#!/usr/bin/env python3
"""
Detect which fpkit component source to import from.

Resolution (first match wins):
  1. "generated" — <componentsDir>/ui.tsx exists locally.
  2. "npm"       — @fpkit/acss is in deps/devDeps and no generated source.
  3. "none"      — neither.

componentsDir comes from .acss-target.json at project root, falling back to
"src/components/fpkit".

The "npm" source path is **deprecated** as of acss-app-builder v0.2.0. It
remains functional through a soft-deprecation window but is scheduled for
removal in a future major version. When source == "npm", the JSON output
adds:
  - "deprecated": true
  - "sunsetVersion": "<captured @fpkit/acss version>"
  - a "reasons" array entry recommending migration via /kit-add

This is a strict JSON-only signal — nothing is written to stderr. Slash
commands consuming this script's output should surface the deprecation in
the chat UI when "deprecated" is true.

Usage:
    python detect_component_source.py [project_root]

Output (JSON to stdout):

    Generated path (preferred):
    {
      "source": "generated",
      "projectRoot": "/abs/path",
      "componentsDir": "src/components/fpkit",
      "importMapHint": "import Button from '../src/components/fpkit/button/button'"
    }

    Deprecated npm path:
    {
      "source": "npm",
      "projectRoot": "/abs/path",
      "componentsDir": "src/components/fpkit",
      "importMapHint": "import { Button } from '@fpkit/acss'",
      "deprecated": true,
      "sunsetVersion": "6.6.0",
      "reasons": [
        "@fpkit/acss npm path is deprecated; vendor components via /kit-add to migrate.",
        "Sunset version: 6.6.0"
      ]
    }

    No source found:
    {
      "source": "none",
      "projectRoot": null,
      "componentsDir": "src/components/fpkit",
      "importMapHint": "",
      "reasons": ["No project root containing react was found."]
    }

Exit code 0 = source detected (generated or npm), 1 = none.
The "deprecated" path returns 0 — the plugin keeps working while users
migrate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional


DEFAULT_COMPONENTS_DIR = "src/components/fpkit"

# Captured @fpkit/acss version that anchors the deprecation window.
# Update this constant when re-running `npm view @fpkit/acss version` for a
# future plugin release. Closest tagged ref in shawn-sandy/acss is
# @fpkit/acss@6.5.0; npm publish 6.6.0 outpaced git tagging.
NPM_SUNSET_VERSION = "6.6.0"


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
        result = {
            "source": source,
            "projectRoot": str(root),
            "componentsDir": components_dir,
            "importMapHint": hint,
        }
    elif has_npm:
        source = "npm"
        hint = "import { Button } from '@fpkit/acss'"
        result = {
            "source": source,
            "projectRoot": str(root),
            "componentsDir": components_dir,
            "importMapHint": hint,
            "deprecated": True,
            "sunsetVersion": NPM_SUNSET_VERSION,
            "reasons": [
                "@fpkit/acss npm path is deprecated; vendor components via /kit-add to migrate.",
                f"Sunset version: {NPM_SUNSET_VERSION}",
            ],
        }
    else:
        source = "none"
        hint = ""
        result = {
            "source": source,
            "projectRoot": str(root),
            "componentsDir": components_dir,
            "importMapHint": hint,
            "reasons": [
                "No fpkit component source found.",
                "Vendor components via /kit-add, or install @fpkit/acss (deprecated).",
            ],
        }

    print(json.dumps(result, indent=2))
    return 0 if source != "none" else 1


if __name__ == "__main__":
    sys.exit(main())
