#!/usr/bin/env python3
"""
Detect the build stack of a React project so /kit-add, /theme-create, and
/utility-add can tailor their integration advice.

Classifies four axes:
  - framework     : vite | next | remix | astro | cra | unknown
  - bundler       : derived from framework (vite | webpack | rollup-vite |
                    rollup | unknown)
  - cssPipeline   : array; any of "tailwind", "sass", "postcss", "css-modules"
  - tsconfig      : bool — tsconfig.json at project root
  - entrypointFile: framework-specific best guess (relative to projectRoot)

The script is read-only. Callers (slash-command SKILLs) are responsible for
persisting the result into .acss-target.json under a "stack" key.

Usage:
    python detect_stack.py [project_root]
    python detect_stack.py --self-test

Output (JSON to stdout, exit 0):

    {
      "source": "detected",
      "projectRoot": "/abs/path",
      "framework": "vite",
      "frameworkVersion": "5.4.0",
      "bundler": "vite",
      "cssPipeline": ["sass", "postcss"],
      "tsconfig": true,
      "entrypointFile": "src/main.tsx",
      "reasons": []
    }

Failure modes (exit 1):

  A. No React project root in any ancestor directory:
    {
      "source": "none",
      "projectRoot": null,
      ...
      "reasons": ["No project root containing react was found."]
    }

  B. Project root found but framework signals all missed:
    {
      "source": "unknown",
      "projectRoot": "/abs/path",
      "framework": "unknown",
      ...
      "reasons": [
        "No vite.config / next.config / remix.config / astro.config found.",
        "No vite / next / @remix-run/* / astro / react-scripts dep in package.json."
      ]
    }
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

DEFAULT_RESULT = {
    "source": "none",
    "projectRoot": None,
    "framework": "unknown",
    "frameworkVersion": None,
    "bundler": "unknown",
    "cssPipeline": [],
    "tsconfig": False,
    "entrypointFile": None,
    "reasons": [],
}

CONFIG_NAMES = {
    "next": ["next.config.js", "next.config.mjs", "next.config.ts"],
    "remix": ["remix.config.js", "remix.config.mjs"],
    "astro": ["astro.config.mjs", "astro.config.ts", "astro.config.js"],
    "vite": ["vite.config.ts", "vite.config.js", "vite.config.mjs"],
}

DEP_NAMES = {
    "next": ["next"],
    "remix": ["@remix-run/react", "@remix-run/node", "@remix-run/serve"],
    "astro": ["astro"],
    "vite": ["vite"],
    "cra": ["react-scripts"],
}

BUNDLER_BY_FRAMEWORK = {
    "vite": "vite",
    "next": "webpack",
    "remix": "vite",
    "astro": "vite",
    "cra": "webpack",
    "unknown": "unknown",
}

ENTRYPOINT_CANDIDATES = {
    "vite": ["src/main.tsx", "src/main.ts", "src/main.jsx", "src/main.js"],
    "cra": ["src/index.tsx", "src/index.ts", "src/index.jsx", "src/index.js"],
    "next": [
        "app/layout.tsx",
        "app/layout.jsx",
        "src/app/layout.tsx",
        "src/app/layout.jsx",
        "pages/_app.tsx",
        "pages/_app.jsx",
        "src/pages/_app.tsx",
        "src/pages/_app.jsx",
    ],
    "remix": ["app/root.tsx", "app/root.jsx"],
    "astro": [],
}


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


def read_package_json(root: Path) -> dict:
    pkg = root / "package.json"
    try:
        return json.loads(pkg.read_text(encoding="utf-8"))
    except Exception:
        return {}


def all_deps(pkg: dict) -> dict:
    return {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}


def detect_framework(root: Path, deps: dict) -> tuple[str, Optional[str], list[str]]:
    """Return (framework, version, reasons). Order: next, remix, astro, vite, cra."""
    reasons: list[str] = []
    for fw in ("next", "remix", "astro", "vite"):
        for cfg in CONFIG_NAMES[fw]:
            if (root / cfg).is_file():
                version = None
                for dep_name in DEP_NAMES[fw]:
                    if dep_name in deps:
                        version = deps[dep_name]
                        break
                return fw, version, reasons
        for dep_name in DEP_NAMES[fw]:
            if dep_name in deps:
                return fw, deps[dep_name], reasons
    if "react-scripts" in deps:
        return "cra", deps["react-scripts"], reasons

    reasons.append(
        "No vite.config / next.config / remix.config / astro.config found."
    )
    reasons.append(
        "No vite / next / @remix-run/* / astro / react-scripts dep in package.json."
    )
    return "unknown", None, reasons


def detect_css_pipeline(root: Path, deps: dict) -> list[str]:
    pipeline: list[str] = []
    if "tailwindcss" in deps:
        pipeline.append("tailwind")
    if "sass" in deps or "sass-embedded" in deps:
        pipeline.append("sass")
    for cfg in ("postcss.config.js", "postcss.config.mjs", "postcss.config.cjs"):
        if (root / cfg).is_file():
            pipeline.append("postcss")
            break
    if has_css_modules(root):
        pipeline.append("css-modules")
    return pipeline


def has_css_modules(root: Path) -> bool:
    src = root / "src"
    if not src.is_dir():
        return False
    for path in src.rglob("*.module.*"):
        if path.suffix in (".css", ".scss", ".sass"):
            return True
    return False


def detect_entrypoint(root: Path, framework: str) -> Optional[str]:
    for rel in ENTRYPOINT_CANDIDATES.get(framework, []):
        if (root / rel).is_file():
            return rel
    if framework == "astro":
        layouts = root / "src" / "layouts"
        if layouts.is_dir():
            for f in sorted(layouts.glob("*.astro")):
                return str(f.relative_to(root))
    return None


def detect_stack(root: Path) -> dict:
    pkg = read_package_json(root)
    deps = all_deps(pkg)
    framework, version, fw_reasons = detect_framework(root, deps)
    pipeline = detect_css_pipeline(root, deps)
    has_tsconfig = (root / "tsconfig.json").is_file()
    entry = detect_entrypoint(root, framework)

    reasons = list(fw_reasons)
    if framework != "unknown" and entry is None:
        reasons.append(
            f"Detected framework={framework} but no known entrypoint file was present — "
            "ask the developer to confirm their entrypoint and persist it under stack.entrypointFile."
        )

    if framework == "unknown" or entry is None:
        source = "unknown"
    else:
        source = "detected"

    return {
        "source": source,
        "projectRoot": str(root),
        "framework": framework,
        "frameworkVersion": version,
        "bundler": BUNDLER_BY_FRAMEWORK[framework],
        "cssPipeline": pipeline,
        "tsconfig": has_tsconfig,
        "entrypointFile": entry,
        "reasons": reasons,
    }


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        return self_test()

    start = Path(args[0]).resolve() if args else Path.cwd()
    root = find_project_root(start)
    if root is None:
        result = dict(DEFAULT_RESULT)
        result["reasons"] = ["No project root containing react was found."]
        print(json.dumps(result, indent=2))
        return 1

    result = detect_stack(root)
    print(json.dumps(result, indent=2))
    return 0 if result["source"] == "detected" else 1


def self_test() -> int:
    import tempfile

    passed = 0
    failed = 0

    def run(
        name: str,
        files: dict,
        expected_framework: str,
        expected_pipeline: Optional[list] = None,
        expected_entry: Optional[str] = None,
        expected_source: Optional[str] = None,
    ) -> None:
        nonlocal passed, failed
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for filename, content in files.items():
                path = root / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            result = detect_stack(root)
            checks = [("framework", expected_framework, result["framework"])]
            if expected_pipeline is not None:
                checks.append(("cssPipeline", expected_pipeline, result["cssPipeline"]))
            if expected_entry is not None:
                checks.append(("entrypointFile", expected_entry, result["entrypointFile"]))
            if expected_source is not None:
                checks.append(("source", expected_source, result["source"]))
            mismatches = [
                f"{key} expected={want!r} got={got!r}"
                for key, want, got in checks
                if want != got
            ]
            if not mismatches:
                print(f"PASS: {name}")
                passed += 1
            else:
                print(f"FAIL: {name} — {'; '.join(mismatches)}")
                failed += 1

    react_pkg = '{"name":"t","dependencies":{"react":"18"}}'

    run(
        "vite.config.ts → vite",
        {"package.json": react_pkg, "vite.config.ts": "", "src/main.tsx": ""},
        "vite",
        expected_entry="src/main.tsx",
    )
    run(
        "next.config.mjs → next (top-level app/)",
        {"package.json": react_pkg, "next.config.mjs": "", "app/layout.tsx": ""},
        "next",
        expected_entry="app/layout.tsx",
    )
    run(
        "next.config.mjs → next (src/app/ layout)",
        {"package.json": react_pkg, "next.config.mjs": "", "src/app/layout.tsx": ""},
        "next",
        expected_entry="src/app/layout.tsx",
    )
    run(
        "next.config.mjs → next (src/pages/_app)",
        {"package.json": react_pkg, "next.config.mjs": "", "src/pages/_app.tsx": ""},
        "next",
        expected_entry="src/pages/_app.tsx",
    )
    run(
        "remix.config.js → remix",
        {"package.json": react_pkg, "remix.config.js": "", "app/root.tsx": ""},
        "remix",
        expected_entry="app/root.tsx",
    )
    run(
        "astro.config.mjs → astro (no layout: source=unknown)",
        {"package.json": react_pkg, "astro.config.mjs": ""},
        "astro",
        expected_source="unknown",
    )
    run(
        "astro.config.mjs → astro (with layout: source=detected)",
        {
            "package.json": react_pkg,
            "astro.config.mjs": "",
            "src/layouts/Base.astro": "",
        },
        "astro",
        expected_entry="src/layouts/Base.astro",
        expected_source="detected",
    )
    run(
        "next detected but no entrypoint → source=unknown",
        {"package.json": react_pkg, "next.config.mjs": ""},
        "next",
        expected_source="unknown",
    )
    run(
        "react-scripts dep → cra",
        {
            "package.json": '{"name":"t","dependencies":{"react":"18","react-scripts":"5"}}',
            "src/index.tsx": "",
        },
        "cra",
        expected_entry="src/index.tsx",
    )
    run(
        "no framework signal → unknown",
        {"package.json": react_pkg},
        "unknown",
    )
    run(
        "vite + sass + tailwind",
        {
            "package.json": (
                '{"name":"t","dependencies":{"react":"18"},'
                '"devDependencies":{"vite":"5","sass":"1","tailwindcss":"3"}}'
            ),
            "src/main.tsx": "",
        },
        "vite",
        expected_pipeline=["tailwind", "sass"],
    )
    run(
        "css-modules detected via *.module.scss",
        {
            "package.json": '{"name":"t","dependencies":{"react":"18","vite":"5"}}',
            "src/main.tsx": "",
            "src/Foo.module.scss": ".foo{}",
        },
        "vite",
        expected_pipeline=["css-modules"],
    )
    run(
        "css-modules detected via *.module.sass",
        {
            "package.json": '{"name":"t","dependencies":{"react":"18","vite":"5"}}',
            "src/main.tsx": "",
            "src/Foo.module.sass": ".foo",
        },
        "vite",
        expected_pipeline=["css-modules"],
    )

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED")
        return 1
    print(f"\nAll {total} self-tests PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
