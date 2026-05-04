#!/usr/bin/env python3
"""
Detect the target directory for static-HTML component output.

The HTML generator (skill: components-html) is intentionally framework-agnostic:
unlike detect_target.py — which walks ancestors looking for a package.json that
declares a React dependency — this script only requires that the caller picks a
project root. Any directory the user can write into is a valid root, including:

    - a static-site project with no package.json at all
    - a server-rendered project (Rails / Django / PHP / etc.)
    - a React project that wants HTML snippets alongside the TSX components

Resolution:
  1. "configured" — .acss-html-target.json exists at projectRoot with a
     componentsHtmlDir field. Foundation file <componentsHtmlDir>/_stateful.js
     does not need to exist yet — first run writes it.
  2. "none"       — neither file exists. Caller (the SKILL.md) prompts for a
     directory and writes the config.

componentsHtmlDir defaults to "components/html" when no config is present.

Usage:
    python detect_html_target.py [project_root]
    python detect_html_target.py --self-test

Output (JSON to stdout):

    Configured (foundation file exists — fully bootstrapped):
    {
      "source": "configured",
      "projectRoot": "/abs/path",
      "componentsHtmlDir": "components/html",
      "foundationPresent": true,
      "reasons": []
    }

    Configured but foundation file not yet copied (still success — exit 0):
    {
      "source": "configured",
      "projectRoot": "/abs/path",
      "componentsHtmlDir": "components/html",
      "foundationPresent": false,
      "reasons": ["_stateful.js not yet copied — first /kit-add-html run will copy it."]
    }

    Not configured (exit 1):
    {
      "source": "none",
      "projectRoot": "/abs/path",
      "componentsHtmlDir": "components/html",
      "foundationPresent": false,
      "reasons": [
        "No .acss-html-target.json found.",
        "First /kit-add-html run will prompt for componentsHtmlDir and write this file."
      ]
    }

Exit code 0 = configured, 1 = none.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


DEFAULT_HTML_DIR = "components/html"
CONFIG_FILENAME = ".acss-html-target.json"
FOUNDATION_FILENAME = "_stateful.js"


def read_html_dir(root: Path) -> tuple[str, bool]:
    """Return (componentsHtmlDir, configured). configured=True when the config
    file exists and parses; False otherwise — the default is then used."""
    target = root / CONFIG_FILENAME
    if target.is_file():
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            chd = data.get("componentsHtmlDir")
            if isinstance(chd, str) and chd.strip():
                return chd.strip(), True
        except Exception:
            pass
    return DEFAULT_HTML_DIR, False


def detect(root: Path) -> dict:
    components_html_dir, configured = read_html_dir(root)
    foundation_present = (root / components_html_dir / FOUNDATION_FILENAME).is_file()

    if configured:
        reasons: list[str] = []
        if not foundation_present:
            reasons.append(
                f"{FOUNDATION_FILENAME} not yet copied — first /kit-add-html run "
                "will copy it."
            )
        return {
            "source": "configured",
            "projectRoot": str(root),
            "componentsHtmlDir": components_html_dir,
            "foundationPresent": foundation_present,
            "reasons": reasons,
        }

    return {
        "source": "none",
        "projectRoot": str(root),
        "componentsHtmlDir": components_html_dir,
        "foundationPresent": foundation_present,
        "reasons": [
            f"No {CONFIG_FILENAME} found.",
            "First /kit-add-html run will prompt for componentsHtmlDir and write "
            "this file.",
        ],
    }


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        return self_test()

    start = Path(args[0]).resolve() if args else Path.cwd()
    result = detect(start)
    print(json.dumps(result, indent=2))
    return 0 if result["source"] == "configured" else 1


def self_test() -> int:
    import tempfile

    passed = 0
    failed = 0

    def run(name: str, files: dict, expect_source: str,
            expect_foundation: bool | None = None,
            expect_reason_substr: str | None = None) -> None:
        nonlocal passed, failed
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for filename, content in files.items():
                p = root / filename
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
            result = detect(root)
            ok = result["source"] == expect_source
            if expect_foundation is not None:
                ok = ok and result["foundationPresent"] == expect_foundation
            if expect_reason_substr is not None:
                ok = ok and any(expect_reason_substr in r for r in result["reasons"])
            if ok:
                print(f"PASS: {name}")
                passed += 1
            else:
                print(
                    f"FAIL: {name} — source={result['source']!r} "
                    f"foundationPresent={result['foundationPresent']!r} "
                    f"reasons={result['reasons']!r}"
                )
                failed += 1

    run(
        "no config file → source=none with default dir",
        {},
        expect_source="none",
        expect_foundation=False,
        expect_reason_substr=f"No {CONFIG_FILENAME} found.",
    )
    run(
        "config present, foundation missing → configured + warning",
        {CONFIG_FILENAME: json.dumps({"componentsHtmlDir": "public/snippets"})},
        expect_source="configured",
        expect_foundation=False,
        expect_reason_substr=f"{FOUNDATION_FILENAME} not yet copied",
    )
    run(
        "config present, foundation present → configured clean",
        {
            CONFIG_FILENAME: json.dumps({"componentsHtmlDir": "public/snippets"}),
            f"public/snippets/{FOUNDATION_FILENAME}": "// stub\n",
        },
        expect_source="configured",
        expect_foundation=True,
    )
    run(
        "malformed config → falls back to default dir, source=none",
        {CONFIG_FILENAME: "not valid json{"},
        expect_source="none",
        expect_reason_substr=f"No {CONFIG_FILENAME} found.",
    )
    run(
        "config has empty componentsHtmlDir → falls back to default, source=none",
        {CONFIG_FILENAME: json.dumps({"componentsHtmlDir": ""})},
        expect_source="none",
    )

    total = passed + failed
    if failed:
        print(f"\n{failed}/{total} self-test(s) FAILED")
        return 1
    print(f"\nAll {total} self-tests PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
