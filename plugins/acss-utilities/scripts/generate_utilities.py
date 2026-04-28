#!/usr/bin/env python3
"""
Generate Tailwind-style atomic CSS utilities from a token source-of-truth.

Reads `utilities.tokens.json` (path via --tokens, or stdin if absent) and
emits CSS. Without --out-dir, writes the concatenated bundle to stdout.
With --out-dir DIR, writes per-family partials and the concatenated bundle:

    DIR/utilities/<family>.css       per-family partials
    DIR/utilities.css                concatenated bundle

Usage:
    python3 generate_utilities.py [--tokens FILE] [--out-dir DIR]
    python3 generate_utilities.py < utilities.tokens.json

Contract: generator/validator (data on stdout, errors on stderr, exit 0/1/2).
Stdlib only.

Class conventions match fpkit/acss upstream:
  - kebab-case selectors, no prefix (`.bg-primary`, `.mt-4`)
  - responsive variants via escaped colon (`.sm\\:hide`) at breakpoints
    sm/md/lg/xl from tokens.breakpoints
  - print:hide for the print media query
  - !important on display/visibility utilities only (composes elsewhere)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Callable, Dict, List

# --- Family ordering: stable concatenation order for the bundle ---------
FAMILY_ORDER = [
    "color-bg", "color-text", "color-border",
    "spacing",
    "display", "flex", "grid",
    "type",
    "radius", "shadow",
    "position", "z-index",
]

# --- Helpers ------------------------------------------------------------

def _important(family: str) -> str:
    """Return ' !important' for utilities that should always win."""
    return " !important" if family == "display" else ""


def _bp_keys(tokens: dict) -> List[str]:
    return list(tokens.get("breakpoints", {}).keys())


def _spacing_value(idx: int, baseline: str) -> str:
    """idx*baseline → CSS calc value. idx=0 → '0'; otherwise '<idx*0.5>rem' style."""
    if idx == 0:
        return "0"
    # baseline is like '0.5rem'; multiply numerically.
    num_part = "".join(c for c in baseline if c.isdigit() or c == ".")
    unit = baseline[len(num_part):] or "rem"
    val = float(num_part) * idx
    # Normalize: trim trailing zeros after decimal, keep ints clean.
    if val == int(val):
        return f"{int(val)}{unit}"
    return f"{val:g}{unit}"


def _section(title: str, body: str) -> str:
    return f"/* {title} */\n{body}".rstrip() + "\n"


def _wrap_responsive(body: str, family: str, tokens: dict, emit_base: Callable[[str], str]) -> str:
    """Append @media blocks with `.bp\\:<class>` variants for each breakpoint."""
    parts = [body]
    for bp in _bp_keys(tokens):
        width = tokens["breakpoints"][bp]
        prefixed = emit_base(bp + r"\:")
        parts.append(f"@media (width >= {width}) {{\n{prefixed}}}")
    return "\n".join(parts)


# --- Family emitters ----------------------------------------------------

def emit_color_bg(tokens: dict) -> str:
    lines = []
    for name, var in tokens["colorRoles"].items():
        lines.append(f".bg-{name} {{ background-color: var({var}, transparent); }}")
    # state -bg variants (mute success-bg, error-bg, etc.)
    for name, var in tokens.get("stateBg", {}).items():
        lines.append(f".bg-{name}-subtle {{ background-color: var({var}, transparent); }}")
    lines.append(".bg-transparent { background-color: transparent; }")
    return _section("color-bg utilities", "\n".join(lines))


def emit_color_text(tokens: dict) -> str:
    lines = []
    for name, var in tokens["colorRoles"].items():
        lines.append(f".text-{name} {{ color: var({var}, currentColor); }}")
    return _section("color-text utilities", "\n".join(lines))


def emit_color_border(tokens: dict) -> str:
    lines = []
    for name, var in tokens["colorRoles"].items():
        lines.append(f".border-{name} {{ border-color: var({var}, currentColor); }}")
    return _section("color-border utilities", "\n".join(lines))


def emit_spacing(tokens: dict) -> str:
    spacing = tokens["spacing"]
    baseline = spacing["baseline"]
    scale = spacing["scale"]
    props = spacing["properties"]
    prop_map = {
        "m": ("margin",),
        "mt": ("margin-top",),
        "mb": ("margin-bottom",),
        "ml": ("margin-left",),
        "mr": ("margin-right",),
        "mx": ("margin-left", "margin-right"),
        "my": ("margin-top", "margin-bottom"),
        "p": ("padding",),
        "pt": ("padding-top",),
        "pb": ("padding-bottom",),
        "pl": ("padding-left",),
        "pr": ("padding-right",),
        "px": ("padding-left", "padding-right"),
        "py": ("padding-top", "padding-bottom"),
        "gap": ("gap",),
    }

    def block(prefix: str = "") -> str:
        out: List[str] = []
        for prop in props:
            css_props = prop_map[prop]
            for v in scale:
                value = _spacing_value(v, baseline)
                rules = "; ".join(f"{p}: {value}" for p in css_props)
                out.append(f".{prefix}{prop}-{v} {{ {rules}; }}")
        return "\n".join(out) + "\n"

    body = block("")
    if tokens["families"]["spacing"].get("responsive"):
        body = _wrap_responsive(body, "spacing", tokens, block)
    return _section("spacing utilities", body)


def emit_display(tokens: dict) -> str:
    imp = _important("display")
    base_classes = [
        ("hide",       f"display: none{imp};"),
        ("show",       f"display: revert{imp};"),
        ("invisible",  f"visibility: hidden{imp};"),
    ]

    def block(prefix: str = "") -> str:
        out = [f".{prefix}{name} {{ {decl} }}" for name, decl in base_classes]
        return "\n".join(out) + "\n"

    body = block("")
    # sr-only utilities (no responsive variants — accessibility primitive).
    body += (
        ".sr-only {\n"
        "  position: absolute; width: 1px; height: 1px;\n"
        "  padding: 0; margin: -1px; overflow: hidden;\n"
        "  clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0;\n"
        "}\n"
        ".sr-only-focusable {\n"
        "  position: absolute; width: 1px; height: 1px;\n"
        "  padding: 0; margin: -1px; overflow: hidden;\n"
        "  clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0;\n"
        "}\n"
        ".sr-only-focusable:focus,\n"
        ".sr-only-focusable:focus-within {\n"
        "  position: static; width: auto; height: auto;\n"
        "  padding: 0; margin: 0; overflow: visible;\n"
        "  clip: auto; white-space: normal;\n"
        "}\n"
    )

    if tokens["families"]["display"].get("responsive"):
        for bp, width in tokens["breakpoints"].items():
            body += f"@media (width >= {width}) {{\n{block(bp + chr(92) + ':')}}}\n"
    body += "@media print { .print\\:hide { display: none !important; } }\n"
    return _section("display utilities", body)


def emit_flex(tokens: dict) -> str:
    base_classes = [
        ("flex",            "display: flex;"),
        ("inline-flex",     "display: inline-flex;"),
        ("flex-row",        "flex-direction: row;"),
        ("flex-row-reverse","flex-direction: row-reverse;"),
        ("flex-col",        "flex-direction: column;"),
        ("flex-col-reverse","flex-direction: column-reverse;"),
        ("flex-wrap",       "flex-wrap: wrap;"),
        ("flex-nowrap",     "flex-wrap: nowrap;"),
        ("flex-1",          "flex: 1 1 0%;"),
        ("flex-auto",       "flex: 1 1 auto;"),
        ("flex-none",       "flex: none;"),
        ("justify-start",   "justify-content: flex-start;"),
        ("justify-end",     "justify-content: flex-end;"),
        ("justify-center",  "justify-content: center;"),
        ("justify-between", "justify-content: space-between;"),
        ("justify-around",  "justify-content: space-around;"),
        ("items-start",     "align-items: flex-start;"),
        ("items-end",       "align-items: flex-end;"),
        ("items-center",    "align-items: center;"),
        ("items-baseline",  "align-items: baseline;"),
        ("items-stretch",   "align-items: stretch;"),
    ]

    def block(prefix: str = "") -> str:
        return "\n".join(f".{prefix}{name} {{ {decl} }}" for name, decl in base_classes) + "\n"

    body = block("")
    if tokens["families"]["flex"].get("responsive"):
        body = _wrap_responsive(body, "flex", tokens, block)
    return _section("flex utilities", body)


def emit_grid(tokens: dict) -> str:
    base_classes = [
        ("grid",        "display: grid;"),
        ("inline-grid", "display: inline-grid;"),
    ]
    base_classes += [
        (f"grid-cols-{n}", f"grid-template-columns: repeat({n}, minmax(0, 1fr));")
        for n in range(1, 13)
    ]
    base_classes += [
        (f"grid-rows-{n}", f"grid-template-rows: repeat({n}, minmax(0, 1fr));")
        for n in range(1, 7)
    ]

    def block(prefix: str = "") -> str:
        return "\n".join(f".{prefix}{name} {{ {decl} }}" for name, decl in base_classes) + "\n"

    body = block("")
    if tokens["families"]["grid"].get("responsive"):
        body = _wrap_responsive(body, "grid", tokens, block)
    return _section("grid utilities", body)


def emit_type(tokens: dict) -> str:
    t = tokens["type"]
    lines: List[str] = []
    for name, size in t["fontSize"].items():
        lines.append(f".text-{name} {{ font-size: {size}; }}")
    for name, weight in t["fontWeight"].items():
        lines.append(f".font-{name} {{ font-weight: {weight}; }}")
    for name, lh in t["leading"].items():
        lines.append(f".leading-{name} {{ line-height: {lh}; }}")
    for align in t["align"]:
        lines.append(f".text-{align} {{ text-align: {align}; }}")
    return _section("type utilities", "\n".join(lines))


def emit_radius(tokens: dict) -> str:
    lines = []
    for name, value in tokens["radius"].items():
        if name == "md":
            # Tailwind convention: bare `.rounded` is the default (md) radius.
            lines.append(f".rounded {{ border-radius: {value}; }}")
        lines.append(f".rounded-{name} {{ border-radius: {value}; }}")
    return _section("radius utilities", "\n".join(lines))


def emit_shadow(tokens: dict) -> str:
    lines = []
    for name, value in tokens["shadow"].items():
        if name == "md":
            lines.append(f".shadow {{ box-shadow: {value}; }}")
        lines.append(f".shadow-{name} {{ box-shadow: {value}; }}")
    return _section("shadow utilities", "\n".join(lines))


def emit_position(tokens: dict) -> str:
    lines = [f".{p} {{ position: {p}; }}" for p in tokens["positions"]]
    return _section("position utilities", "\n".join(lines))


def emit_zindex(tokens: dict) -> str:
    lines = []
    for v in tokens["zIndex"]:
        lines.append(f".z-{v} {{ z-index: {v}; }}")
    return _section("z-index utilities", "\n".join(lines))


# --- Dispatcher ---------------------------------------------------------

EMITTERS: Dict[str, Callable[[dict], str]] = {
    "color-bg":     emit_color_bg,
    "color-text":   emit_color_text,
    "color-border": emit_color_border,
    "spacing":      emit_spacing,
    "display":      emit_display,
    "flex":         emit_flex,
    "grid":         emit_grid,
    "type":         emit_type,
    "radius":       emit_radius,
    "shadow":       emit_shadow,
    "position":     emit_position,
    "z-index":      emit_zindex,
}


def emit_family(family: str, tokens: dict) -> str:
    if family not in EMITTERS:
        raise KeyError(family)
    return EMITTERS[family](tokens)


def emit_bundle_header(tokens: dict) -> str:
    return (
        "/*\n"
        f" * acss-utilities v{tokens['version']}\n"
        f" * Generated from utilities.tokens.json\n"
        f" * Mirrors fpkit upstream: {tokens['fpkitUpstream']}\n"
        " *\n"
        " * Do not edit by hand. Regenerate via `generate_utilities.py`.\n"
        " */\n\n"
    )


def emit_bundle(tokens: dict) -> Dict[str, str]:
    """Return {family_name: css} plus a synthetic 'bundle' key."""
    out: Dict[str, str] = {}
    for fam in FAMILY_ORDER:
        cfg = tokens["families"].get(fam, {})
        if not cfg.get("enabled", True):
            continue
        out[fam] = emit_family(fam, tokens)
    bundle_parts = [emit_bundle_header(tokens)]
    for fam in FAMILY_ORDER:
        if fam in out:
            bundle_parts.append(out[fam])
    out["bundle"] = "\n".join(bundle_parts)
    return out


# --- I/O ----------------------------------------------------------------

def load_tokens(path: str | None) -> dict:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return json.loads(sys.stdin.read())


def write_outputs(out_dir: str, parts: Dict[str, str]) -> List[str]:
    out_root = Path(out_dir)
    fam_dir = out_root / "utilities"
    fam_dir.mkdir(parents=True, exist_ok=True)
    written: List[str] = []
    for name, css in parts.items():
        if name == "bundle":
            target = out_root / "utilities.css"
        else:
            target = fam_dir / f"{name}.css"
        target.write_text(css, encoding="utf-8")
        written.append(str(target))
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, add_help=True)
    parser.add_argument("--tokens", help="Path to utilities.tokens.json (else stdin)")
    parser.add_argument("--out-dir", help="Write per-family partials + bundle to DIR")
    args = parser.parse_args()

    try:
        tokens = load_tokens(args.tokens)
    except FileNotFoundError as e:
        print(f"tokens file not found: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"invalid tokens JSON: {e}", file=sys.stderr)
        return 2

    try:
        parts = emit_bundle(tokens)
    except KeyError as e:
        print(f"unknown family or missing token key: {e}", file=sys.stderr)
        return 1

    if args.out_dir:
        written = write_outputs(args.out_dir, parts)
        for p in written:
            print(p)
    else:
        sys.stdout.write(parts["bundle"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
