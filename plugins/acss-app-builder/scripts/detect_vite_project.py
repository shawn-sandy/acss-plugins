#!/usr/bin/env python3
"""
Detect a Vite + React project and locate its entry file.

Usage:
    python detect_vite_project.py [project_root]

Output (JSON to stdout):
    {
      "isVite": true,
      "isReact": true,
      "isTypeScript": true,
      "projectRoot": "/abs/path",
      "entry": "src/main.tsx",
      "viteConfig": "vite.config.ts" | null,
      "reasons": ["..."]
    }

Exit code 0 = detected, 1 = not detected (with reason in JSON).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional


def find_project_root(start: Path) -> Optional[Path]:
    """Nearest ancestor with a package.json that depends on react."""
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


def find_vite_config(root: Path) -> Optional[str]:
    for name in ("vite.config.ts", "vite.config.js", "vite.config.mjs"):
        if (root / name).is_file():
            return name
    return None


SCRIPT_SRC_RE = re.compile(
    r'<script[^>]+type=["\']module["\'][^>]+src=["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def find_entry_from_index_html(root: Path) -> Optional[str]:
    html = root / "index.html"
    if not html.is_file():
        return None
    text = html.read_text(encoding="utf-8", errors="replace")
    m = SCRIPT_SRC_RE.search(text)
    if not m:
        return None
    src = m.group(1).lstrip("/")
    return src if (root / src).is_file() else None


def main() -> int:
    start = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    reasons: list[str] = []

    root = find_project_root(start)
    if root is None:
        print(json.dumps({
            "isVite": False, "isReact": False, "isTypeScript": False,
            "projectRoot": None, "entry": None, "viteConfig": None,
            "reasons": ["No ancestor package.json depending on react was found."],
        }))
        return 1

    pkg = json.loads((root / "package.json").read_text(encoding="utf-8"))
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    is_react = "react" in deps
    is_vite = "vite" in deps
    is_ts = "typescript" in deps or (root / "tsconfig.json").is_file()

    if not is_react:
        reasons.append("react missing from dependencies.")
    if not is_vite:
        reasons.append("vite missing from dependencies.")

    vite_config = find_vite_config(root)
    entry = find_entry_from_index_html(root)
    if entry is None:
        # fallback hint, not assumed
        reasons.append("Could not derive entry from index.html <script src>; specify manually.")

    detected = is_vite and is_react
    print(json.dumps({
        "isVite": is_vite,
        "isReact": is_react,
        "isTypeScript": is_ts,
        "projectRoot": str(root),
        "entry": entry,
        "viteConfig": vite_config,
        "reasons": reasons,
    }, indent=2))
    return 0 if detected else 1


if __name__ == "__main__":
    sys.exit(main())
