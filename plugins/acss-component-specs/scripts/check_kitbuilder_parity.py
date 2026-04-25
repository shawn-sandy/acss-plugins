#!/usr/bin/env python3
"""
check_kitbuilder_parity.py — Verify that a spec-rendered component matches the
kit-builder bundled reference for the same component name.

Compares the spec-rendered file (from .acss-staging/react/) against what the
kit-builder reference doc implies should be generated, using a header-tolerant
byte comparison (first 5 lines stripped from both sides).

Designed to run as a pre-commit hook when specs/*.md is modified.

Usage:
    python check_kitbuilder_parity.py button
    python check_kitbuilder_parity.py button card

Output: JSON to stdout.
Exit 0 = parity confirmed. Exit 1 = drift detected or missing files.
"""

import json
import os
import re
import sys
from pathlib import Path


def _fail(reasons):
    print(json.dumps({"ok": False, "data": None, "reasons": reasons}))
    sys.exit(1)


def _strip_header(lines, n=5):
    """Strip first n lines (generated stamp, copyright, etc.) for comparison."""
    return lines[n:] if len(lines) > n else []


def _normalize(text):
    """Normalize whitespace for comparison — collapse runs of blank lines."""
    lines = text.splitlines()
    normalized = []
    prev_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        normalized.append(line.rstrip())
        prev_blank = is_blank
    return '\n'.join(normalized).strip()


def check_component(component):
    """
    Check parity for one component.
    Returns (ok: bool, reasons: list[str])
    """
    reasons = []

    # Locate staged React output
    staging_tsx = Path(f'.acss-staging/react/{component}/{component}.tsx')
    staging_scss = Path(f'.acss-staging/react/{component}/{component}.scss')

    # Locate kit-builder reference doc
    plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT', '')
    if plugin_root:
        kit_ref = Path(plugin_root) / '../acss-kit-builder/skills/acss-kit-builder/references/components' / f'{component}.md'
    else:
        # Fallback: resolve relative to this script's plugin root
        kit_ref = Path(__file__).parent.parent.parent / \
                  'acss-kit-builder/skills/acss-kit-builder/references/components' / f'{component}.md'

    if not staging_tsx.exists():
        reasons.append(f"Staged file not found: {staging_tsx}. Run /spec-render {component} --target=react first.")
        return False, reasons

    if not kit_ref.exists():
        reasons.append(f"Kit-builder reference not found: {kit_ref}. Parity check skipped (not a failure).")
        # Not a failure — kit-builder may not have this component
        return True, reasons

    # Extract the SCSS Pattern block from the kit-builder reference doc
    kit_text = kit_ref.read_text(encoding='utf-8')
    scss_block_m = re.search(
        r'## SCSS Pattern\s*```scss\s*(.*?)```',
        kit_text,
        re.DOTALL
    )
    if not scss_block_m:
        reasons.append(f"No '## SCSS Pattern' code block found in {kit_ref}. Skipping parity check.")
        return True, reasons

    kit_scss = scss_block_m.group(1).strip()

    # Read staged SCSS
    staged_scss = staging_scss.read_text(encoding='utf-8') if staging_scss.exists() else ''
    staged_lines = staged_scss.splitlines()
    staged_stripped = _strip_header(staged_lines)

    kit_lines = kit_scss.splitlines()
    kit_stripped = _strip_header(kit_lines, n=0)  # kit ref has no header lines

    staged_norm = _normalize('\n'.join(staged_stripped))
    kit_norm = _normalize('\n'.join(kit_stripped))

    if staged_norm == kit_norm:
        return True, []

    # Find first differing line for a helpful error
    staged_final = staged_norm.splitlines()
    kit_final = kit_norm.splitlines()

    first_diff = None
    for i, (a, b) in enumerate(zip(staged_final, kit_final)):
        if a != b:
            first_diff = i + 1
            break
    if first_diff is None and len(staged_final) != len(kit_final):
        first_diff = min(len(staged_final), len(kit_final)) + 1

    reasons.append(
        f"SCSS parity drift for '{component}': staged SCSS differs from kit-builder reference "
        f"at line ~{first_diff} (after stripping headers and normalizing whitespace). "
        f"Run /spec-render {component} --target=react and review the diff."
    )
    return False, reasons


def main():
    components = sys.argv[1:]
    if not components:
        _fail(["Usage: check_kitbuilder_parity.py <component> [<component2> ...]"])

    all_ok = True
    all_reasons = []
    results = {}

    for comp in components:
        ok, reasons = check_component(comp)
        results[comp] = {"ok": ok, "reasons": reasons}
        if not ok:
            all_ok = False
            all_reasons.extend(reasons)

    print(json.dumps({
        "ok": all_ok,
        "data": {"results": results},
        "reasons": all_reasons,
    }, indent=2))
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
