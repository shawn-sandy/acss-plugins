#!/usr/bin/env python3
"""Validate the SCSS contract for extracted acss-kit component styles.

Walks the directory passed as argv[1], reads every .scss file, strips
SCSS-only single-line comments (`// ...`) that tinycss2 cannot parse,
parses the remaining content with tinycss2, then asserts:

  - Every var(--color-*, ...), var(--font-*, ...), and var(--space-*, ...)
    reference includes a fallback. This is the load-bearing contract:
    components must render correctly when consumed in projects whose
    theme CSS hasn't loaded yet.

The looser checks originally proposed (bare-px detection, cross-file
class conflicts) were dropped after the initial run revealed the
existing references legitimately use px (e.g. 999px for pill shapes,
1-2px borders) and intentionally share class names across components
for inheritance (icon-button extends button via .btn). Re-enable those
checks if a future contract change makes them load-bearing.

Output contract: detector style — JSON to stdout, "reasons" array
populated on failure, exit 0 on success and 1 on logical failure (2 on
usage / IO errors). Mirrors the shape of detect_target.py.
"""

import json
import re
import sys
from pathlib import Path

try:
    import tinycss2
except ImportError:
    print(
        json.dumps(
            {
                "ok": False,
                "reasons": [
                    "tinycss2 not installed: run "
                    "`pip3 install --user tinycss2`",
                ],
            },
        ),
    )
    sys.exit(2)


VAR_NO_FALLBACK_RE = re.compile(
    r"var\(\s*--(?:color|font|space)-[A-Za-z0-9_-]+\s*\)",
)


def strip_scss_comments(content: str) -> str:
    """Remove SCSS `//` single-line comments so tinycss2 can parse the rest."""
    out_lines = []
    for line in content.splitlines():
        idx = -1
        in_string = False
        quote = ""
        i = 0
        while i < len(line) - 1:
            ch = line[i]
            if in_string:
                if ch == quote and line[i - 1] != "\\":
                    in_string = False
            elif ch in ("'", '"'):
                in_string = True
                quote = ch
            elif ch == "/" and line[i + 1] == "/":
                idx = i
                break
            i += 1
        out_lines.append(line if idx < 0 else line[:idx])
    return "\n".join(out_lines)


def serialize_value(rule):
    return tinycss2.serialize(rule.content) if rule.content else ""


def collect_failures_for_file(path: Path):
    failures = []
    raw = path.read_text(encoding="utf-8")
    stripped = strip_scss_comments(raw)
    rules = tinycss2.parse_stylesheet(
        stripped, skip_whitespace=True, skip_comments=True,
    )

    for rule in rules:
        if rule.type == "error":
            failures.append(
                f"{path.name}: parser error at line {rule.source_line}: {rule.message}",
            )
            continue
        if rule.type != "qualified-rule":
            continue

        body = serialize_value(rule)

        for match in VAR_NO_FALLBACK_RE.finditer(body):
            failures.append(
                f"{path.name}: var() without fallback: {match.group(0)}",
            )

    return failures


def main() -> int:
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "ok": False,
                    "reasons": ["usage: validate_components.py <extracted-dir>"],
                },
            ),
        )
        return 2

    target = Path(sys.argv[1])
    if not target.is_dir():
        print(
            json.dumps(
                {
                    "ok": False,
                    "reasons": [f"not a directory: {target}"],
                },
            ),
        )
        return 2

    failures = []

    scss_files = sorted(target.rglob("*.scss"))
    if not scss_files:
        print(
            json.dumps(
                {
                    "ok": False,
                    "reasons": [f"no .scss files under {target}"],
                },
            ),
        )
        return 1

    for path in scss_files:
        failures.extend(collect_failures_for_file(path))

    payload = {
        "ok": len(failures) == 0,
        "filesScanned": len(scss_files),
        "reasons": failures,
    }
    print(json.dumps(payload, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
