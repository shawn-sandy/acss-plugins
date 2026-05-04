#!/usr/bin/env python3
"""
Verify that static-HTML artifacts written by /kit-add-html are referenced by
the user's pages.

Detector contract: read-only, JSON to stdout, exit 0 when every generated
artifact is referenced by at least one page, exit 1 with populated `reasons`
array otherwise.

Reads .acss-html-target.json for componentsHtmlDir. Then, for each generated
file under that directory:

    - *.scss / *.css       → expect a <link rel="stylesheet"> or @import that
                             names the file in any *.html / *.htm / *.css /
                             *.scss page under projectRoot
    - *.js                 → expect a <script src="..."> reference
    - *.html               → these are content fragments, not entrypoints —
                             they are not checked for inclusion (the user is
                             expected to copy/paste or server-side-include
                             them). They are still listed in `checks` for
                             visibility.

Usage:
    python verify_html_integration.py [project_root]
    python verify_html_integration.py --self-test

Output (JSON to stdout):

    All wired up:
    {
      "ok": true,
      "projectRoot": "/abs/path",
      "componentsHtmlDir": "components/html",
      "checks": [
        {"artifact": "button.scss", "kind": "style", "imported": true},
        {"artifact": "dialog.js",   "kind": "script", "imported": true},
        {"artifact": "button.html", "kind": "snippet", "imported": null}
      ],
      "reasons": []
    }

    Missing references:
    {
      "ok": false,
      ...
      "reasons": [
        "button.scss not referenced by any *.html or *.css under <root> — add: <link rel=\"stylesheet\" href=\"components/html/button.scss\">"
      ]
    }
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional


CONFIG_FILENAME = ".acss-html-target.json"
DEFAULT_HTML_DIR = "components/html"

# Skip these directories when scanning for page references — they are
# build artifacts, dependencies, or VCS metadata, never the user's source.
SKIP_DIRS = {"node_modules", "dist", "build", ".git", ".next", ".cache", "out"}

PAGE_EXTENSIONS = (".html", ".htm", ".css", ".scss", ".sass", ".vue", ".svelte",
                   ".njk", ".liquid", ".erb", ".php", ".jsx", ".tsx", ".astro",
                   ".md", ".mdx")


def iter_page_files(root: Path):
    """Yield every page-ish file under root that might reference an artifact,
    skipping build/dep directories."""
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.suffix.lower() in PAGE_EXTENSIONS:
            yield p


def read_target(root: Path) -> dict:
    target = root / CONFIG_FILENAME
    if target.is_file():
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def is_referenced(basename: str, pages: list[Path]) -> bool:
    """A simple substring scan — basename must appear inside a known
    reference syntax. We avoid full HTML parsing on purpose; the goal is
    "did the user wire it up at all?", not strict validation."""
    needle = basename
    for page in pages:
        try:
            text = page.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if needle not in text:
            continue
        # Look for any line that both names the artifact and looks like a
        # reference (link/script/import). This trades precision for resilience
        # against templating engines and bundler-rewritten paths.
        for line in text.splitlines():
            if needle not in line:
                continue
            stripped = line.strip().lower()
            if any(token in stripped for token in (
                "<link",
                "<script",
                "@import",
                "@use",
                "@forward",
                "import",
                "require(",
                "url(",
            )):
                return True
    return False


def classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".scss", ".css", ".sass"):
        return "style"
    if suffix in (".js", ".mjs"):
        return "script"
    if suffix in (".html", ".htm"):
        return "snippet"
    return "other"


def verify(root: Path) -> dict:
    target = read_target(root)
    components_html_dir = target.get("componentsHtmlDir") or DEFAULT_HTML_DIR
    artifacts_dir = root / components_html_dir

    if not artifacts_dir.is_dir():
        return {
            "ok": False,
            "projectRoot": str(root),
            "componentsHtmlDir": components_html_dir,
            "checks": [],
            "reasons": [
                f"componentsHtmlDir {components_html_dir} does not exist — "
                "run /kit-add-html first."
            ],
        }

    pages = [p for p in iter_page_files(root)
             if not p.is_relative_to(artifacts_dir)]

    checks: list[dict] = []
    reasons: list[str] = []

    for artifact in sorted(artifacts_dir.rglob("*")):
        if not artifact.is_file():
            continue
        # Skip the foundation helper itself — it is imported by the
        # generated *.js modules, not by user pages.
        if artifact.name == "_stateful.js":
            continue
        kind = classify(artifact)
        if kind == "snippet":
            checks.append({
                "artifact": artifact.name,
                "kind": kind,
                "imported": None,
            })
            continue
        if kind == "other":
            continue

        imported = is_referenced(artifact.name, pages)
        checks.append({
            "artifact": artifact.name,
            "kind": kind,
            "imported": imported,
        })
        if not imported:
            ref_path = f"{components_html_dir}/{artifact.name}"
            if kind == "style":
                hint = f'<link rel="stylesheet" href="{ref_path}">'
            else:
                hint = f'<script type="module" src="{ref_path}"></script>'
            reasons.append(
                f"{artifact.name} not referenced by any page under {root.name}/ "
                f"— add: {hint}"
            )

    return {
        "ok": not reasons,
        "projectRoot": str(root),
        "componentsHtmlDir": components_html_dir,
        "checks": checks,
        "reasons": reasons,
    }


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        return self_test()

    start = Path(args[0]).resolve() if args else Path.cwd()
    result = verify(start)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def self_test() -> int:
    import tempfile

    passed = 0
    failed = 0

    def run(name: str, files: dict, expect_ok: bool,
            expect_reason_substr: Optional[str] = None) -> None:
        nonlocal passed, failed
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for filename, content in files.items():
                p = root / filename
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
            result = verify(root)
            ok = result["ok"] == expect_ok
            if expect_reason_substr is not None:
                ok = ok and any(expect_reason_substr in r
                                for r in result["reasons"])
            if ok:
                print(f"PASS: {name}")
                passed += 1
            else:
                print(
                    f"FAIL: {name} — ok={result['ok']!r} "
                    f"reasons={result['reasons']!r}"
                )
                failed += 1

    target = json.dumps({"componentsHtmlDir": "components/html"})

    run(
        "componentsHtmlDir missing → reason explains why",
        {CONFIG_FILENAME: target},
        expect_ok=False,
        expect_reason_substr="does not exist",
    )
    run(
        "stylesheet linked from index.html → ok",
        {
            CONFIG_FILENAME: target,
            "components/html/button.scss": ".btn{}",
            "index.html": (
                "<!doctype html><html><head>"
                '<link rel="stylesheet" href="components/html/button.scss">'
                "</head></html>"
            ),
        },
        expect_ok=True,
    )
    run(
        "stylesheet not linked anywhere → reason w/ <link> hint",
        {
            CONFIG_FILENAME: target,
            "components/html/button.scss": ".btn{}",
            "index.html": "<!doctype html><html></html>",
        },
        expect_ok=False,
        expect_reason_substr='<link rel="stylesheet"',
    )
    run(
        "script wired via <script src> → ok",
        {
            CONFIG_FILENAME: target,
            "components/html/dialog.js": "export {}",
            "index.html": (
                '<!doctype html><html><body>'
                '<script type="module" src="components/html/dialog.js"></script>'
                '</body></html>'
            ),
        },
        expect_ok=True,
    )
    run(
        "script not wired → reason w/ <script> hint",
        {
            CONFIG_FILENAME: target,
            "components/html/dialog.js": "export {}",
            "index.html": "<!doctype html><html></html>",
        },
        expect_ok=False,
        expect_reason_substr='<script type="module"',
    )
    run(
        "*.html snippets are not checked for inclusion (kind=snippet)",
        {
            CONFIG_FILENAME: target,
            "components/html/button.html": "<button class=\"btn\"></button>",
        },
        expect_ok=True,
    )
    run(
        "_stateful.js is excluded from checks (it is imported by other JS, "
        "not by pages)",
        {
            CONFIG_FILENAME: target,
            "components/html/_stateful.js": "export const wireDisabled = ()=>{};",
        },
        expect_ok=True,
    )
    run(
        "stylesheet linked via @import in user SCSS counts as wired",
        {
            CONFIG_FILENAME: target,
            "components/html/button.scss": ".btn{}",
            "src/styles/main.scss": '@import "../../components/html/button.scss";',
        },
        expect_ok=True,
    )
    run(
        "node_modules copy of artifact does not count",
        {
            CONFIG_FILENAME: target,
            "components/html/button.scss": ".btn{}",
            # Adversarial: a stale link inside node_modules should be ignored
            "node_modules/old/index.html": (
                '<link rel="stylesheet" href="components/html/button.scss">'
            ),
        },
        expect_ok=False,
        expect_reason_substr="button.scss not referenced",
    )

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED")
        return 1
    print(f"\nAll {total} self-tests PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
