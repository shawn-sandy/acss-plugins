#!/usr/bin/env python3
"""
Convert theme CSS files into a theme.tokens.json file.

Usage:
    python css_to_tokens.py <light.css> [dark.css] [brand-*.css ...]
    python css_to_tokens.py --dir=<dir>   (scans for light.css, dark.css, brand-*.css)

Output: JSON to stdout conforming to assets/theme.schema.json.

Exit codes: 0 = success, 2 = usage/IO error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PALETTE_FILE_RE = re.compile(r"^(light|dark|brand-[\w-]+)\.css$")
VAR_DECL_RE = re.compile(r"^\s*(--[a-z0-9-]+)\s*:\s*([^;]+);", re.IGNORECASE | re.MULTILINE)
VAR_REF_RE = re.compile(r"var\(\s*(--[a-z0-9-]+)\s*(?:,\s*([^)]+))?\)")
HEX_RE = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})")

# Roles relevant to theme tokens (ignore component-level tokens)
COLOR_ROLE_RE = re.compile(r"^--color-")

# Brand files only override these roles
BRAND_ROLES = {
    "--color-primary", "--color-primary-hover",
    "--color-focus-ring", "--color-brand-accent",
}


def _parse_vars(text: str) -> dict[str, str]:
    return {m.group(1): m.group(2).strip() for m in VAR_DECL_RE.finditer(text)}


def _resolve_hex(name: str, vars_: dict[str, str], depth: int = 3) -> str | None:
    if depth < 0 or name not in vars_:
        return None
    raw = vars_[name]
    m = HEX_RE.search(raw)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return "#" + h
    m = VAR_REF_RE.search(raw)
    if m:
        resolved = _resolve_hex(m.group(1), vars_, depth - 1)
        if resolved:
            return resolved
        if m.group(2):
            fm = HEX_RE.search(m.group(2))
            if fm:
                h = fm.group(1)
                if len(h) == 3:
                    h = "".join(c * 2 for c in h)
                return "#" + h
    return None


def _extract_selector_blocks(text: str) -> dict[str, str]:
    """Split CSS into blocks by selector. Returns {selector: block_text}."""
    # Match :root { ... } and [data-theme="dark"] { ... }
    pattern = re.compile(
        r'(:root|\[data-theme=["\']dark["\']\])\s*\{([^}]*)\}',
        re.DOTALL | re.IGNORECASE,
    )
    blocks: dict[str, str] = {}
    for m in pattern.finditer(text):
        sel = m.group(1).strip()
        key = "dark" if "dark" in sel.lower() else "light"
        blocks[key] = blocks.get(key, "") + m.group(2)
    return blocks


def _parse_palette_from_block(block: str) -> dict[str, str]:
    vars_ = _parse_vars(block)
    palette: dict[str, str] = {}
    for name, _ in vars_.items():
        if COLOR_ROLE_RE.match(name):
            resolved = _resolve_hex(name, vars_)
            if resolved:
                palette[name] = resolved
    return palette


def _process_file(path: Path) -> tuple[str, dict]:
    """Return (file_type, data). file_type is 'light', 'dark', or 'brand-<name>'."""
    text = path.read_text(encoding="utf-8")
    stem = path.stem  # e.g. 'light', 'dark', 'brand-forest'

    if stem in ("light", "dark"):
        blocks = _extract_selector_blocks(text)
        if stem in blocks:
            return stem, _parse_palette_from_block(blocks[stem])
        # Fallback: parse all vars if selector not found
        return stem, _parse_palette_from_block(text)

    if stem.startswith("brand-"):
        name = stem[len("brand-"):]
        blocks = _extract_selector_blocks(text)
        overrides: dict = {}
        for mode_key, block in blocks.items():
            palette = _parse_palette_from_block(block)
            filtered = {k: v for k, v in palette.items() if k in BRAND_ROLES}
            if filtered:
                overrides[mode_key] = filtered
        return f"brand-{name}", overrides

    # Unknown — parse everything as a flat dict
    return stem, _parse_palette_from_block(text)


def main() -> int:
    args = sys.argv[1:]
    scan_dir: Path | None = None
    file_paths: list[Path] = []

    for a in args:
        if a.startswith("--dir="):
            scan_dir = Path(a.split("=", 1)[1])
        elif not a.startswith("--"):
            file_paths.append(Path(a))

    if scan_dir:
        for p in scan_dir.rglob("*.css"):
            if PALETTE_FILE_RE.match(p.name):
                file_paths.append(p)

    if not file_paths:
        print("usage: css_to_tokens.py <light.css> [dark.css] [brand-*.css ...] | --dir=<dir>",
              file=sys.stderr)
        return 2

    tokens: dict = {"modes": {}, "brands": {}}

    for path in file_paths:
        if not path.exists():
            print(f"not found: {path}", file=sys.stderr)
            return 2
        file_type, data = _process_file(path)
        if file_type in ("light", "dark"):
            tokens["modes"][file_type] = data
        elif file_type.startswith("brand-"):
            name = file_type[len("brand-"):]
            tokens["brands"][name] = data

    if not tokens["brands"]:
        del tokens["brands"]

    print(json.dumps(tokens, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
