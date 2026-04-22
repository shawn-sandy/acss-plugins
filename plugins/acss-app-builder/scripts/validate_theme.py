#!/usr/bin/env python3
"""
Validate a theme CSS file for WCAG AA contrast on semantic role pairs.

Scope (v0.1):
  - Only runs against files named `light.css`, `dark.css`, or `brand-*.css`.
  - Resolves one level of var() references to find hex-literal terminal values.
  - Checks a fixed set of semantic pairs against WCAG contrast thresholds.

Usage:
    python validate_theme.py <file-or-dir>

Exit codes:
    0 = no failures
    1 = at least one contrast pair below threshold
    2 = usage / IO error

No external dependencies — stdlib only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


PALETTE_FILE_RE = re.compile(r"^(light|dark|brand-[\w-]+)\.css$")

# semantic pairs to validate (fg, bg, min_ratio)
PAIRS = [
    ("--color-text", "--color-background", 4.5),
    ("--color-primary", "--color-background", 3.0),
    ("--color-text-inverse", "--color-primary", 4.5),
]

VAR_DECL_RE = re.compile(r"^\s*(--[a-z0-9-]+)\s*:\s*([^;]+);", re.IGNORECASE | re.MULTILINE)
VAR_REF_RE = re.compile(r"var\(\s*(--[a-z0-9-]+)\s*(?:,\s*([^)]+))?\)")
HEX_RE = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})")


def parse_vars(text: str) -> dict[str, str]:
    return {m.group(1): m.group(2).strip() for m in VAR_DECL_RE.finditer(text)}


def resolve_to_hex(name: str, vars_: dict[str, str], depth: int = 3) -> str | None:
    if depth < 0 or name not in vars_:
        return None
    raw = vars_[name]
    m = HEX_RE.search(raw)
    if m:
        return "#" + m.group(1)
    m = VAR_REF_RE.search(raw)
    if m:
        referenced = m.group(1)
        fallback = m.group(2)
        resolved = resolve_to_hex(referenced, vars_, depth - 1)
        if resolved:
            return resolved
        if fallback:
            fm = HEX_RE.search(fallback)
            if fm:
                return "#" + fm.group(1)
    return None


def hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r / 255.0, g / 255.0, b / 255.0)


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(hex_fg: str, hex_bg: str) -> float:
    l1 = relative_luminance(hex_to_rgb(hex_fg))
    l2 = relative_luminance(hex_to_rgb(hex_bg))
    light, dark = (l1, l2) if l1 > l2 else (l2, l1)
    return (light + 0.05) / (dark + 0.05)


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    vars_ = parse_vars(text)

    for fg_name, bg_name, threshold in PAIRS:
        fg = resolve_to_hex(fg_name, vars_)
        bg = resolve_to_hex(bg_name, vars_)
        if not fg or not bg:
            # not an error — just skip pairs that don't resolve to hex in this file
            continue
        ratio = contrast(fg, bg)
        if ratio < threshold:
            errors.append(
                f"{path}: {fg_name} on {bg_name} = {ratio:.2f}:1 (required {threshold}:1) "
                f"[resolved fg={fg}, bg={bg}]"
            )
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_theme.py <file-or-dir>", file=sys.stderr)
        return 2

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"not found: {target}", file=sys.stderr)
        return 2

    files: list[Path] = []
    if target.is_file():
        if PALETTE_FILE_RE.match(target.name):
            files.append(target)
    else:
        for p in target.rglob("*.css"):
            if PALETTE_FILE_RE.match(p.name):
                files.append(p)

    if not files:
        print("no palette files found (expected light.css, dark.css, or brand-*.css)")
        return 0

    all_errors: list[str] = []
    for f in files:
        all_errors.extend(check_file(f))

    if all_errors:
        print("Contrast failures:")
        for e in all_errors:
            print("  " + e)
        return 1

    print(f"validate_theme: OK ({len(files)} palette file(s) checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
