#!/usr/bin/env python3
"""
Verify the user's React entrypoint actually imports the assets that
/kit-add, /theme-create, and /utility-add wrote into the project.

Detector contract: read-only, JSON to stdout, exit 0 when every wired-up
artifact is imported, exit 1 with populated `reasons` array otherwise.

Reads .acss-target.json for componentsDir, utilitiesDir, and
stack.entrypointFile. Then, for each artifact that exists on disk, checks
whether it is imported (by basename) in the entrypoint. Bridge ordering
relative to utilities.css is line-number compared.

Usage:
    python verify_integration.py [project_root]
    python verify_integration.py --self-test

Output (JSON to stdout):

    All wired up:
    {
      "ok": true,
      "projectRoot": "/abs/path",
      "entrypointFile": "src/main.tsx",
      "checks": [
        {"artifact": "token-bridge.css", "imported": true},
        {"artifact": "utilities.css",    "imported": true},
        {"artifact": "light.css",        "imported": true}
      ],
      "reasons": []
    }

    Missing wires:
    {
      "ok": false,
      "projectRoot": "/abs/path",
      "entrypointFile": "src/main.tsx",
      "checks": [...],
      "reasons": [
        "token-bridge.css written to src/styles/ but not imported in src/main.tsx — add: import './styles/token-bridge.css';",
        "utilities.css imported but appears before token-bridge.css — bridge must load first."
      ]
    }
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

DEFAULT_COMPONENTS_DIR = "src/components/fpkit"
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


def read_target(root: Path) -> dict:
    target = root / ".acss-target.json"
    if target.is_file():
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def find_import_line(text: str, basename: str) -> Optional[int]:
    """Return 1-based line number of the first import line referencing basename."""
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if not (stripped.startswith("import") or stripped.startswith("require(")):
            continue
        if basename in stripped:
            return idx
    return None


def find_any_use(root: Path, components_dir: str) -> bool:
    """Return True if any *.tsx/*.ts/*.jsx/*.js under src/ references componentsDir."""
    src = root / "src"
    if not src.is_dir():
        return False
    needle = components_dir.replace("\\", "/")
    last_segment = needle.rstrip("/").split("/")[-1] or needle
    for ext in ("*.tsx", "*.ts", "*.jsx", "*.js"):
        for path in src.rglob(ext):
            try:
                txt = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if last_segment in txt:
                return True
    return False


def verify(root: Path) -> dict:
    target = read_target(root)
    components_dir = target.get("componentsDir") or DEFAULT_COMPONENTS_DIR
    utilities_dir = target.get("utilitiesDir") or DEFAULT_UTILITIES_DIR
    stack = target.get("stack") or {}
    entrypoint_rel = stack.get("entrypointFile")

    checks: list[dict] = []
    reasons: list[str] = []

    if not entrypoint_rel:
        return {
            "ok": False,
            "projectRoot": str(root),
            "entrypointFile": None,
            "checks": checks,
            "reasons": [
                "stack.entrypointFile not set in .acss-target.json — run detect_stack.py and persist its result first."
            ],
        }

    entrypoint_path = root / entrypoint_rel
    if not entrypoint_path.is_file():
        return {
            "ok": False,
            "projectRoot": str(root),
            "entrypointFile": entrypoint_rel,
            "checks": checks,
            "reasons": [
                f"Entrypoint {entrypoint_rel} does not exist — re-run detect_stack.py."
            ],
        }

    entry_text = entrypoint_path.read_text(encoding="utf-8", errors="ignore")

    bridge_path = root / utilities_dir / "token-bridge.css"
    utilities_path = root / utilities_dir / "utilities.css"
    bridge_line: Optional[int] = None
    utilities_line: Optional[int] = None

    if bridge_path.is_file():
        bridge_line = find_import_line(entry_text, "token-bridge.css")
        imported = bridge_line is not None
        checks.append({"artifact": "token-bridge.css", "imported": imported})
        if not imported:
            reasons.append(
                f"token-bridge.css written to {utilities_dir}/ but not imported in "
                f"{entrypoint_rel} — add: import './{utilities_dir.removeprefix('src/')}/token-bridge.css';"
            )

    if utilities_path.is_file():
        utilities_line = find_import_line(entry_text, "utilities.css")
        imported = utilities_line is not None
        checks.append({"artifact": "utilities.css", "imported": imported})
        if not imported:
            reasons.append(
                f"utilities.css written to {utilities_dir}/ but not imported in "
                f"{entrypoint_rel} — add: import './{utilities_dir.removeprefix('src/')}/utilities.css';"
            )

    if (
        bridge_line is not None
        and utilities_line is not None
        and utilities_line < bridge_line
    ):
        reasons.append(
            "utilities.css is imported before token-bridge.css — the bridge must load first or "
            "utility classes will reference undefined CSS variables."
        )

    theme_files = []
    for candidate in ("light.css", "dark.css"):
        for base in (
            root / "src" / "styles" / "theme" / candidate,
            root / "src" / "styles" / candidate,
            root / "src" / candidate,
            root / utilities_dir / candidate,
        ):
            if base.is_file():
                theme_files.append((candidate, base))
                break
    if theme_files:
        any_imported = any(
            find_import_line(entry_text, name) is not None for name, _ in theme_files
        )
        checks.append({"artifact": "theme css", "imported": any_imported})
        if not any_imported:
            names = ", ".join(sorted({name for name, _ in theme_files}))
            reasons.append(
                f"Theme files present ({names}) but no theme CSS imported in {entrypoint_rel}."
            )

    ui_path = root / components_dir / "ui.tsx"
    if ui_path.is_file():
        used = find_any_use(root, components_dir)
        checks.append({"artifact": f"{components_dir}/ui.tsx", "imported": used})
        if not used:
            reasons.append(
                f"{components_dir}/ui.tsx is vendored but no source file under src/ references "
                f"{components_dir} — components are not yet wired into the app."
            )

    return {
        "ok": not reasons,
        "projectRoot": str(root),
        "entrypointFile": entrypoint_rel,
        "checks": checks,
        "reasons": reasons,
    }


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        return self_test()

    start = Path(args[0]).resolve() if args else Path.cwd()
    root = find_project_root(start)
    if root is None:
        print(json.dumps({
            "ok": False,
            "projectRoot": None,
            "entrypointFile": None,
            "checks": [],
            "reasons": ["No project root containing react was found."],
        }, indent=2))
        return 1

    result = verify(root)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def self_test() -> int:
    import tempfile

    passed = 0
    failed = 0

    def run(name: str, files: dict, expect_ok: bool, expect_reason_substr: Optional[str] = None) -> None:
        nonlocal passed, failed
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for filename, content in files.items():
                p = root / filename
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
            result = verify(root)
            ok_match = result["ok"] == expect_ok
            substr_match = True
            if expect_reason_substr is not None:
                substr_match = any(expect_reason_substr in r for r in result["reasons"])
            if ok_match and substr_match:
                print(f"PASS: {name}")
                passed += 1
            else:
                print(
                    f"FAIL: {name} — ok={result['ok']} reasons={result['reasons']!r}"
                )
                failed += 1

    pkg = '{"name":"t","dependencies":{"react":"18"}}'
    target_with_entry = json.dumps({
        "componentsDir": "src/components/fpkit",
        "utilitiesDir": "src/styles",
        "stack": {"entrypointFile": "src/main.tsx"},
    })

    run(
        "missing entrypointFile in target",
        {
            "package.json": pkg,
            ".acss-target.json": json.dumps({"componentsDir": "src/components/fpkit"}),
        },
        expect_ok=False,
        expect_reason_substr="stack.entrypointFile not set",
    )
    run(
        "bridge written but not imported",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": "console.log('no imports')\n",
            "src/styles/token-bridge.css": ":root{}",
        },
        expect_ok=False,
        expect_reason_substr="token-bridge.css",
    )
    run(
        "bridge imported, no other artifacts",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": "import './styles/token-bridge.css';\n",
            "src/styles/token-bridge.css": ":root{}",
        },
        expect_ok=True,
    )
    run(
        "utilities imported before bridge → ordering reason",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": (
                "import './styles/utilities.css';\n"
                "import './styles/token-bridge.css';\n"
            ),
            "src/styles/token-bridge.css": ":root{}",
            "src/styles/utilities.css": ".m-1{}",
        },
        expect_ok=False,
        expect_reason_substr="bridge must load first",
    )
    run(
        "ui.tsx vendored but never used",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": "console.log('hi')\n",
            "src/components/fpkit/ui.tsx": "export const UI = {};",
        },
        expect_ok=False,
        expect_reason_substr="ui.tsx is vendored",
    )
    run(
        "ui.tsx used in a feature file",
        {
            "package.json": pkg,
            ".acss-target.json": target_with_entry,
            "src/main.tsx": "import App from './app';\n",
            "src/app.tsx": "import { UI } from './components/fpkit/ui';\n",
            "src/components/fpkit/ui.tsx": "export const UI = {};",
        },
        expect_ok=True,
    )

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED")
        return 1
    print(f"\nAll {total} self-tests PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
