#!/usr/bin/env python3
"""
Detect candidate CSS / SCSS entry files in a React project so /setup can wire
the generated theme imports (light.css, dark.css) into the project's main
stylesheet.

Detector contract: read-only, JSON to stdout, exit 0 when at least one
candidate exists, exit 1 with `source: "none"` and populated `reasons` when
nothing matches.

Resolution: walks a fixed candidate list relative to project_root in priority
order. For every file that exists on disk, scans for existing imports (by
basename) of the artifacts /setup and /utility-* may write — light.css,
dark.css, token-bridge.css, utilities.css. Recognises JS/TS `import` /
`require(` and Sass `@import` / `@use` lines.

Usage:
    python detect_css_entry.py [project_root]
    python detect_css_entry.py --self-test

Output (JSON to stdout):

    At least one candidate found (exit 0):
    {
      "source": "detected",
      "projectRoot": "/abs/path",
      "candidates": [
        {
          "path": "src/styles/index.scss",
          "imports": {
            "light.css": 3,
            "dark.css": null,
            "token-bridge.css": null,
            "utilities.css": null
          }
        }
      ],
      "reasons": []
    }

    No candidate found (exit 1):
    {
      "source": "none",
      "projectRoot": "/abs/path",
      "candidates": [],
      "reasons": [
        "No CSS or SCSS entry file found at any of the standard locations.",
        "Pick a path or create one (e.g. src/styles/index.scss) and re-run /setup."
      ]
    }
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

# Priority-ordered candidate paths relative to project_root. Earlier entries
# win — the SKILL still asks the user when multiple exist, but tooling and
# downstream consumers can rely on this order when a single deterministic
# choice is needed.
CANDIDATES: tuple[str, ...] = (
    "src/styles/index.scss",
    "src/styles/index.css",
    "src/styles/main.scss",
    "src/styles/main.css",
    "src/styles/globals.scss",
    "src/styles/globals.css",
    "src/index.css",
    "src/index.scss",
    "src/main.css",
    "src/main.scss",
    "src/App.css",
    "src/App.scss",
    "src/global.css",
    "src/global.scss",
    "app/globals.css",
    "styles/globals.css",
)

TRACKED_BASENAMES: tuple[str, ...] = (
    "light.css",
    "dark.css",
    "token-bridge.css",
    "utilities.css",
)

_IMPORT_PREFIXES: tuple[str, ...] = (
    "import",
    "require(",
    "@import",
    "@use",
    "@forward",
)


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


def find_import_line(text: str, basename: str) -> Optional[int]:
    """Return 1-based line number of the first import line referencing basename.

    Recognises JS/TS (`import`, `require(`) and Sass (`@import`, `@use`,
    `@forward`) statements.
    """
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if not any(stripped.startswith(prefix) for prefix in _IMPORT_PREFIXES):
            continue
        if basename in stripped:
            return idx
    return None


def scan_imports(path: Path) -> dict[str, Optional[int]]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {name: None for name in TRACKED_BASENAMES}
    return {name: find_import_line(text, name) for name in TRACKED_BASENAMES}


def collect_candidates(root: Path) -> list[dict]:
    found: list[dict] = []
    for rel in CANDIDATES:
        path = root / rel
        if path.is_file():
            found.append({"path": rel, "imports": scan_imports(path)})
    return found


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        return self_test()

    start = Path(args[0]).resolve() if args else Path.cwd()
    root = find_project_root(start)
    if root is None:
        print(json.dumps({
            "source": "none",
            "projectRoot": None,
            "candidates": [],
            "reasons": ["No project root containing react was found."],
        }, indent=2))
        return 1

    candidates = collect_candidates(root)
    if not candidates:
        print(json.dumps({
            "source": "none",
            "projectRoot": str(root),
            "candidates": [],
            "reasons": [
                "No CSS or SCSS entry file found at any of the standard locations.",
                "Pick a path or create one (e.g. src/styles/index.scss) and re-run /setup.",
            ],
        }, indent=2))
        return 1

    print(json.dumps({
        "source": "detected",
        "projectRoot": str(root),
        "candidates": candidates,
        "reasons": [],
    }, indent=2))
    return 0


def self_test() -> int:
    import tempfile

    passed = 0
    failed = 0

    def run(name: str, files: dict, expect_source: str, expect_paths: Optional[list[str]] = None,
            expect_imports: Optional[dict[str, dict[str, Optional[int]]]] = None) -> None:
        nonlocal passed, failed
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for filename, content in files.items():
                p = root / filename
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
            candidates = collect_candidates(root)
            source = "detected" if candidates else "none"
            ok = source == expect_source
            if expect_paths is not None:
                ok = ok and [c["path"] for c in candidates] == expect_paths
            if expect_imports is not None:
                for path, expected in expect_imports.items():
                    matched = next((c for c in candidates if c["path"] == path), None)
                    if matched is None or matched["imports"] != expected:
                        ok = False
                        break
            if ok:
                print(f"PASS: {name}")
                passed += 1
            else:
                print(f"FAIL: {name} — candidates={candidates!r}")
                failed += 1

    pkg = '{"name":"t","dependencies":{"react":"18"}}'

    run(
        "no css/scss anywhere → source none",
        {"package.json": pkg, "src/main.tsx": "export {}\n"},
        expect_source="none",
    )
    run(
        "single src/index.css → one candidate, no imports",
        {
            "package.json": pkg,
            "src/index.css": "body { margin: 0; }\n",
        },
        expect_source="detected",
        expect_paths=["src/index.css"],
        expect_imports={"src/index.css": {
            "light.css": None, "dark.css": None,
            "token-bridge.css": None, "utilities.css": None,
        }},
    )
    run(
        "scss with @import light.css already wired",
        {
            "package.json": pkg,
            "src/styles/index.scss": (
                "@charset \"UTF-8\";\n"
                "@import \"./theme/light.css\";\n"
                "@import \"./theme/dark.css\";\n"
            ),
        },
        expect_source="detected",
        expect_paths=["src/styles/index.scss"],
        expect_imports={"src/styles/index.scss": {
            "light.css": 2, "dark.css": 3,
            "token-bridge.css": None, "utilities.css": None,
        }},
    )
    run(
        "multiple candidates → priority order preserved",
        {
            "package.json": pkg,
            "src/styles/index.scss": "// scss\n",
            "src/index.css": "body{}\n",
            "src/App.css": "#app{}\n",
        },
        expect_source="detected",
        expect_paths=["src/styles/index.scss", "src/index.css", "src/App.css"],
    )
    run(
        "next-style app/globals.css picked up",
        {
            "package.json": pkg,
            "app/globals.css": "html{}\n",
        },
        expect_source="detected",
        expect_paths=["app/globals.css"],
    )
    run(
        "@use is recognised as an import-bearing line",
        {
            "package.json": pkg,
            "src/styles/main.scss": (
                "@use \"./theme/light.css\";\n"
                "body { color: black; }\n"
            ),
        },
        expect_source="detected",
        expect_paths=["src/styles/main.scss"],
        expect_imports={"src/styles/main.scss": {
            "light.css": 1, "dark.css": None,
            "token-bridge.css": None, "utilities.css": None,
        }},
    )

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED")
        return 1
    print(f"\nAll {total} self-tests PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
