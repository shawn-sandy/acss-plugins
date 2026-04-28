"""
Shared OKLCH ↔ sRGB conversion helpers (CSS Color 4 matrices).

Used by ``generate_palette.py`` and ``oklch_shift.py``. Stdlib only —
no external dependencies. Underscore prefix marks this as internal:
no CLI entry point, no detector contract.

Public surface:
- ``hex_to_oklch(hex_str) -> (L, C, H)``
- ``oklch_to_hex(L, C, H) -> "#rrggbb"`` (clamps chroma to stay in sRGB gamut)
- ``in_gamut(L, C, H) -> bool``
"""
from __future__ import annotations

import math


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
    """Convert OKLCH to hex, clamping chroma to stay in sRGB gamut.

    Defensive clamps:
    - ``L`` is clamped to ``[0.0, 1.0]`` up front, so the iterative
      chroma-reduction loop always operates on a valid lightness.
    - ``C`` is clamped to ``>= 0``.
    - When all 100 reduction steps fail to find an in-gamut color, we
      return an achromatic hex at the requested lightness directly
      instead of recursing — preventing infinite recursion if numeric
      issues somehow leave even ``C=0`` out of gamut.
    """
    L = max(0.0, min(1.0, L))
    C = max(0.0, C)

    def _achromatic_hex(L_clamped: float) -> str:
        # OKLab → linear sRGB on the neutral axis (a = b = 0): the M2
        # inverse gives l_ = m_ = s_ = L, then cubing yields linear-light
        # r = g = b = L ** 3. Apply gamma encoding to get the sRGB byte.
        lv = max(0.0, min(1.0, L_clamped ** 3))
        gv = round(_gamma(lv) * 255)
        return f"#{gv:02x}{gv:02x}{gv:02x}"

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
        if C == 0.0:
            # Already achromatic and still failing the gamut check —
            # synthesize a neutral gray at the requested lightness
            # directly so we never recurse into the same code path.
            return _achromatic_hex(L)
        C = max(0.0, C - 0.01)
    # Final fallback: achromatic at the (clamped) target lightness.
    return _achromatic_hex(L)


def in_gamut(L: float, C: float, H: float) -> bool:
    """True iff (L, C, H) maps cleanly into sRGB without chroma clamping.

    Uses the same matrix path as ``oklch_to_hex`` but skips the iterative
    chroma reduction. Also enforces a sensible lightness range
    [0.0, 1.0] — values outside that always fail.
    """
    if not (0.0 <= L <= 1.0):
        return False
    a = C * math.cos(math.radians(H))
    b = C * math.sin(math.radians(H))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    lv, mv, sv = l_ ** 3, m_ ** 3, s_ ** 3
    r =  4.0767416621 * lv - 3.3077115913 * mv + 0.2309699292 * sv
    g = -1.2684380046 * lv + 2.6097574011 * mv - 0.3413193965 * sv
    bl = -0.0041960863 * lv - 0.7034186147 * mv + 1.7076147010 * sv
    return all(-0.0001 <= x <= 1.0001 for x in (r, g, bl))
