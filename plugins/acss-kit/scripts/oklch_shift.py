#!/usr/bin/env python3
"""
Shift a hex color in OKLCH space and emit the new hex.

Usage:
    oklch_shift.py <hex> [--hue=±deg] [--chroma=×float] [--lightness=±float]

Examples:
    oklch_shift.py "#2563eb" --hue=8           # rotate hue +8°
    oklch_shift.py "#2563eb" --chroma=0.75     # multiply chroma by 0.75
    oklch_shift.py "#2563eb" --lightness=-0.06 # subtract 0.06 from L

Output: JSON to stdout — { "hex", "oklch": [L, C, H], "shifted": [L, C, H], "reasons": [] }
Exit codes: 0 = success, 1 = logical failure (post-shift out of gamut, etc.), 2 = usage / IO error.

Stdlib only — no external dependencies.
"""
from __future__ import annotations

import json
import re
import sys

from _oklch import hex_to_oklch, in_gamut, oklch_to_hex


HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def _parse_arg(arg: str, prefix: str) -> float | None:
    if not arg.startswith(prefix):
        return None
    raw = arg[len(prefix):].strip()
    if not raw:
        raise ValueError(f"missing value for {prefix.rstrip('=')}")
    return float(raw)


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("usage: oklch_shift.py <hex> [--hue=±deg] [--chroma=×float] [--lightness=±float]", file=sys.stderr)
        return 2

    seed_raw = args[0]
    if not HEX_RE.match(seed_raw):
        print(f"invalid hex color: {seed_raw}", file=sys.stderr)
        return 2

    seed = seed_raw if seed_raw.startswith("#") else "#" + seed_raw
    if len(seed) == 4:
        seed = "#" + "".join(c * 2 for c in seed[1:])

    hue_delta: float = 0.0
    chroma_factor: float = 1.0
    lightness_delta: float = 0.0

    for a in args[1:]:
        try:
            v = _parse_arg(a, "--hue=")
            if v is not None:
                hue_delta = v
                continue
            v = _parse_arg(a, "--chroma=")
            if v is not None:
                chroma_factor = v
                continue
            v = _parse_arg(a, "--lightness=")
            if v is not None:
                lightness_delta = v
                continue
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 2
        print(f"unknown argument: {a}", file=sys.stderr)
        return 2

    reasons: list[str] = []

    L0, C0, H0 = hex_to_oklch(seed)

    L1 = L0 + lightness_delta
    C1 = C0 * chroma_factor
    H1 = (H0 + hue_delta) % 360

    # Lightness clamp [0.0, 1.0] is a hard gamut floor/ceiling; surface it.
    if L1 < 0.0:
        reasons.append(f"lightness out of gamut: {L1:.4f} < 0.0 (clamped to 0.0)")
        L1 = 0.0
    if L1 > 1.0:
        reasons.append(f"lightness out of gamut: {L1:.4f} > 1.0 (clamped to 1.0)")
        L1 = 1.0
    # Chroma must stay non-negative.
    if C1 < 0.0:
        reasons.append(f"chroma negative after shift: {C1:.4f} (clamped to 0.0)")
        C1 = 0.0

    if not in_gamut(L1, C1, H1):
        reasons.append(
            f"shifted color out of sRGB gamut at (L={L1:.4f}, C={C1:.4f}, H={H1:.2f}); "
            f"oklch_to_hex will reduce chroma to fit"
        )

    new_hex = oklch_to_hex(L1, C1, H1)
    Lp, Cp, Hp = hex_to_oklch(new_hex)

    result = {
        "input": seed,
        "hex": new_hex,
        "oklch": [round(Lp, 6), round(Cp, 6), round(Hp, 4)],
        "shifted": [round(L1, 6), round(C1, 6), round(H1, 4)],
        "delta": {
            "hue": hue_delta,
            "chroma": chroma_factor,
            "lightness": lightness_delta,
        },
        "reasons": reasons,
    }
    print(json.dumps(result, indent=2))
    return 1 if reasons else 0


if __name__ == "__main__":
    sys.exit(main())
