#!/usr/bin/env python3
"""
Generate a full semantic role palette from a seed hex color using OKLCH.

Usage:
    python generate_palette.py <hex-color> [--mode=light|dark|both|brand]

Output: JSON to stdout.
Exit codes: 0 = success, 1 = palette failure (non-empty "reasons"), 2 = usage/IO error.
"""
from __future__ import annotations

import json
import math
import re
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# OKLCH ↔ sRGB conversion (CSS Color 4 matrices — no external dependencies)
# ---------------------------------------------------------------------------

def _linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gamma(c: float) -> float:
    return c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1.0 / 2.4)) - 0.055


def hex_to_oklch(hex_str: str) -> tuple[float, float, float]:
    """Return (L, C, H) in OKLCH from a hex color string."""
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0
    # Gamma decode
    r, g, b = _linear(r), _linear(g), _linear(b)
    # Linear sRGB → LMS (M1)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    # Cube root
    l_, m_, s_ = l ** (1.0 / 3.0), m ** (1.0 / 3.0), s ** (1.0 / 3.0)
    # LMS^(1/3) → Oklab (M2)
    L =  0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a =  1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b_ = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    C = math.sqrt(a * a + b_ * b_)
    H = math.degrees(math.atan2(b_, a)) % 360
    return (L, C, H)


def oklch_to_hex(L: float, C: float, H: float) -> str:
    """Convert OKLCH to hex, clamping chroma to stay in sRGB gamut."""
    for _ in range(100):
        a = C * math.cos(math.radians(H))
        b = C * math.sin(math.radians(H))
        # Oklab → LMS^(1/3) (M2 inverse)
        l_ = L + 0.3963377774 * a + 0.2158037573 * b
        m_ = L - 0.1055613458 * a - 0.0638541728 * b
        s_ = L - 0.0894841775 * a - 1.2914855480 * b
        # Cube
        lv, mv, sv = l_ ** 3, m_ ** 3, s_ ** 3
        # LMS → linear sRGB (M1 inverse)
        r =  4.0767416621 * lv - 3.3077115913 * mv + 0.2309699292 * sv
        g = -1.2684380046 * lv + 2.6097574011 * mv - 0.3413193965 * sv
        b_ = -0.0041960863 * lv - 0.7034186147 * mv + 1.7076147010 * sv
        # Check gamut
        if all(-0.0001 <= x <= 1.0001 for x in (r, g, b_)):
            r = max(0.0, min(1.0, r))
            g = max(0.0, min(1.0, g))
            b_ = max(0.0, min(1.0, b_))
            ri = round(_gamma(r) * 255)
            gi = round(_gamma(g) * 255)
            bi = round(_gamma(b_) * 255)
            return f"#{ri:02x}{gi:02x}{bi:02x}"
        C = max(0.0, C - 0.01)
    # Fallback: achromatic at target lightness
    return oklch_to_hex(L, 0.0, H)


def _hex_luminance(hex_str: str) -> float:
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0
    r, g, b = _linear(r), _linear(g), _linear(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(fg: str, bg: str) -> float:
    l1, l2 = _hex_luminance(fg), _hex_luminance(bg)
    light, dark = (l1, l2) if l1 > l2 else (l2, l1)
    return (light + 0.05) / (dark + 0.05)


# ---------------------------------------------------------------------------
# Palette generation
# ---------------------------------------------------------------------------

def _blend_hue(seed_h: float, target_h: float, weight: float = 0.7) -> float:
    """Blend seed hue toward target hue with given weight (0=seed, 1=target)."""
    diff = (target_h - seed_h + 180) % 360 - 180
    return (seed_h + diff * weight) % 360


def _lightest_passing(C: float, H: float, bg: str, min_ratio: float) -> Optional[float]:
    """Highest L (lightest color) where contrast(color, bg) >= min_ratio.
    Used for light-mode primaries vs white: returns the most vibrant-looking primary that still passes."""
    lo, hi = 0.25, 0.90
    if _contrast(oklch_to_hex(lo, C, H), bg) < min_ratio:
        return None  # even the darkest option fails
    if _contrast(oklch_to_hex(hi, C, H), bg) >= min_ratio:
        return hi  # even the lightest option passes
    for _ in range(50):
        mid = (lo + hi) / 2
        if _contrast(oklch_to_hex(mid, C, H), bg) >= min_ratio:
            lo = mid  # passes — try going lighter
        else:
            hi = mid  # too light — go darker
        if hi - lo < 0.001:
            break
    return lo


def _darkest_passing(C: float, H: float, bg: str, min_ratio: float) -> Optional[float]:
    """Lowest L (darkest color) where contrast(color, bg) >= min_ratio.
    Used for dark-mode primaries vs dark bg: returns the most saturated-looking primary that still passes."""
    lo, hi = 0.30, 0.95
    if _contrast(oklch_to_hex(hi, C, H), bg) < min_ratio:
        return None  # even the lightest option fails
    if _contrast(oklch_to_hex(lo, C, H), bg) >= min_ratio:
        return lo  # even the darkest option passes
    for _ in range(50):
        mid = (lo + hi) / 2
        if _contrast(oklch_to_hex(mid, C, H), bg) >= min_ratio:
            hi = mid  # passes — try going darker
        else:
            lo = mid  # too dark — go lighter
        if hi - lo < 0.001:
            break
    return hi


def _generate_light(L: float, C: float, H: float) -> tuple[dict[str, str], list[str]]:
    reasons: list[str] = []
    bg = "#ffffff"
    surface = oklch_to_hex(0.97, min(C * 0.3, 0.02), H)
    surface_raised = "#ffffff"
    border = oklch_to_hex(0.91, min(C * 0.15, 0.015), H)
    border_strong = oklch_to_hex(0.86, min(C * 0.15, 0.015), H)

    # Primary: lightest color where white text-inverse achieves ≥4.5:1 on it
    # 4.5:1 target also satisfies the 3.0:1 primary-vs-background pair
    pL = _lightest_passing(min(C, 0.20), H, bg, 4.5)
    if pL is None:
        reasons.append("Cannot find a gamut-safe primary with 3.0:1 contrast vs white for this hue.")
        pL = 0.42
    primary = oklch_to_hex(pL, min(C, 0.20), H)
    primary_hover = oklch_to_hex(max(0.20, pL - 0.08), min(C, 0.20), H)
    focus_ring = primary

    text = oklch_to_hex(0.10, min(C * 0.15, 0.015), H)
    text_muted_L = _lightest_passing(min(C * 0.10, 0.01), H, bg, 4.5)
    text_muted = oklch_to_hex(text_muted_L or 0.38, min(C * 0.10, 0.01), H)
    text_inverse = "#ffffff"

    success = oklch_to_hex(0.40, 0.15, 145.0)
    warning = oklch_to_hex(0.40, 0.15, 75.0)
    danger  = oklch_to_hex(0.40, 0.15, 25.0)
    info    = primary

    palette = {
        "--color-background":    bg,
        "--color-surface":       surface,
        "--color-surface-raised":surface_raised,
        "--color-text":          text,
        "--color-text-muted":    text_muted,
        "--color-text-inverse":  text_inverse,
        "--color-border":        border,
        "--color-border-strong": border_strong,
        "--color-primary":       primary,
        "--color-primary-hover": primary_hover,
        "--color-success":       success,
        "--color-warning":       warning,
        "--color-danger":        danger,
        "--color-info":          info,
        "--color-focus-ring":    focus_ring,
    }
    return palette, reasons


def _generate_dark(L: float, C: float, H: float) -> tuple[dict[str, str], list[str]]:
    reasons: list[str] = []
    bg = oklch_to_hex(0.10, min(C * 0.15, 0.015), H)
    surface = oklch_to_hex(0.14, min(C * 0.15, 0.015), H)
    surface_raised = oklch_to_hex(0.19, min(C * 0.15, 0.015), H)
    border = oklch_to_hex(0.23, min(C * 0.20, 0.025), H)
    border_strong = oklch_to_hex(0.30, min(C * 0.20, 0.025), H)

    # Primary on dark: darkest color where dark text-inverse achieves ≥4.5:1 on it
    # bg doubles as text-inverse in dark mode; 4.5:1 also satisfies the 3.0:1 pair
    pL = _darkest_passing(min(C, 0.20), H, bg, 4.5)
    if pL is None:
        reasons.append("Cannot find a gamut-safe dark-mode primary with 3.0:1 contrast for this hue.")
        pL = 0.78
    primary = oklch_to_hex(pL, min(C, 0.20), H)
    primary_hover = oklch_to_hex(min(0.95, pL + 0.08), min(C, 0.20), H)
    focus_ring = primary

    text = oklch_to_hex(0.96, min(C * 0.05, 0.005), H)
    text_muted = oklch_to_hex(0.78, min(C * 0.05, 0.008), H)
    text_inverse = bg

    success = oklch_to_hex(0.72, 0.15, 145.0)
    warning = oklch_to_hex(0.78, 0.15, 75.0)
    danger  = oklch_to_hex(0.72, 0.15, 25.0)
    info    = primary

    palette = {
        "--color-background":    bg,
        "--color-surface":       surface,
        "--color-surface-raised":surface_raised,
        "--color-text":          text,
        "--color-text-muted":    text_muted,
        "--color-text-inverse":  text_inverse,
        "--color-border":        border,
        "--color-border-strong": border_strong,
        "--color-primary":       primary,
        "--color-primary-hover": primary_hover,
        "--color-success":       success,
        "--color-warning":       warning,
        "--color-danger":        danger,
        "--color-info":          info,
        "--color-focus-ring":    focus_ring,
    }
    return palette, reasons


def _generate_brand(L: float, C: float, H: float) -> tuple[dict[str, str], list[str]]:
    """Generate only primary/accent overrides for a brand preset."""
    reasons: list[str] = []
    pL_light = _lightest_passing(min(C, 0.20), H, "#ffffff", 3.0)
    dark_bg = oklch_to_hex(0.10, min(C * 0.15, 0.015), H)
    pL_dark = _darkest_passing(min(C, 0.20), H, dark_bg, 3.0)
    if not pL_light or not pL_dark:
        reasons.append("Cannot find gamut-safe brand primary for this hue.")
    pL_light = pL_light or 0.42
    pL_dark = pL_dark or 0.78
    light_primary = oklch_to_hex(pL_light, min(C, 0.20), H)
    light_hover = oklch_to_hex(max(0.20, pL_light - 0.08), min(C, 0.20), H)
    dark_primary = oklch_to_hex(pL_dark, min(C, 0.20), H)
    dark_hover = oklch_to_hex(min(0.95, pL_dark + 0.08), min(C, 0.20), H)
    return {
        "light": {
            "--color-primary":       light_primary,
            "--color-primary-hover": light_hover,
            "--color-focus-ring":    light_primary,
        },
        "dark": {
            "--color-primary":       dark_primary,
            "--color-primary-hover": dark_hover,
            "--color-focus-ring":    dark_primary,
        },
    }, reasons


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("usage: generate_palette.py <hex-color> [--mode=light|dark|both|brand]", file=sys.stderr)
        return 2

    seed_raw = args[0]
    mode = "both"
    for a in args[1:]:
        if a.startswith("--mode="):
            mode = a.split("=", 1)[1].strip()

    if mode not in ("light", "dark", "both", "brand"):
        print(f"unknown mode '{mode}'; expected light|dark|both|brand", file=sys.stderr)
        return 2

    m = HEX_RE.match(seed_raw.lstrip("#").rjust(len(seed_raw)))
    if not m:
        m = HEX_RE.match(seed_raw)
    if not m:
        print(f"invalid hex color: {seed_raw}", file=sys.stderr)
        return 2

    seed = "#" + m.group(1)
    if len(m.group(1)) == 3:
        seed = "#" + "".join(c * 2 for c in m.group(1))

    try:
        oklch = hex_to_oklch(seed)
    except Exception as e:
        print(f"color conversion error: {e}", file=sys.stderr)
        return 2

    L, C, H = oklch
    all_reasons: list[str] = []
    result: dict = {"seed": seed, "reasons": []}

    if mode == "brand":
        overrides, reasons = _generate_brand(L, C, H)
        all_reasons.extend(reasons)
        result["brand_overrides"] = overrides
    else:
        modes: dict = {}
        if mode in ("light", "both"):
            palette, reasons = _generate_light(L, C, H)
            all_reasons.extend(reasons)
            modes["light"] = palette
        if mode in ("dark", "both"):
            palette, reasons = _generate_dark(L, C, H)
            all_reasons.extend(reasons)
            modes["dark"] = palette
        result["modes"] = modes

    result["reasons"] = all_reasons
    print(json.dumps(result, indent=2))
    return 1 if all_reasons else 0


if __name__ == "__main__":
    sys.exit(main())
