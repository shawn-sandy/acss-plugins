# Palette Generation Algorithm

`scripts/generate_palette.py` converts a seed hex color into a full semantic role palette using the OKLCH color space.

## Why OKLCH

HSL lightness is not perceptually uniform: a hue-shift at L=50% produces very different perceived lightness depending on hue (yellow is much brighter than blue at the same HSL L value). OKLCH's L axis is perceptually uniform, so "increase L by 0.15" produces the same perceived lightness step regardless of hue. This makes it possible to compute contrast-safe palettes algorithmically without manual tuning per-hue.

## Conversion chain

```
hex → sRGB (0-1) → linear sRGB → LMS (M1 matrix) → LMS^(1/3) → Oklab (M2 matrix) → OKLCH
```

Inverse (OKLCH → hex):
```
OKLCH → Oklab → LMS^(1/3) → LMS → linear sRGB → sRGB → clamp(0,1) → hex
```

Both conversions are implemented in `generate_palette.py` using the CSS Color 4 matrices (no external dependencies).

## Lightness targets

These L values are chosen to guarantee WCAG AA contrast by construction against the fixed background anchors.

### Light mode (bg anchor: #ffffff, L≈1.0)

| Role | Target L | Rationale |
|---|---|---|
| `--color-primary` | 0.42–0.48 | Achieves ≥3.0:1 vs white background |
| `--color-primary-hover` | L − 0.08 | Darker hover; preserves hue |
| `--color-focus-ring` | same as primary | Reuses primary |
| `--color-text` | 0.10 | ~16:1 vs white (same hue as seed, desaturated) |
| `--color-text-muted` | 0.35 | ~7:1 vs white |
| `--color-text-inverse` | 0.98 (white) | On primary bg |
| `--color-background` | 1.00 (#ffffff) | Fixed anchor |
| `--color-surface` | 0.97 | Slight warm/cool tint toward seed hue |
| `--color-surface-raised` | 1.00 (#ffffff) | Same as background |
| `--color-border` | 0.92 | Low-saturation tint |
| `--color-border-strong` | 0.87 | Slightly darker |

### Dark mode (bg anchor: oklch(0.10 0.02 seed-hue), L≈0.10)

| Role | Target L | Rationale |
|---|---|---|
| `--color-primary` | 0.75–0.80 | Achieves ≥3.0:1 vs dark background |
| `--color-primary-hover` | L + 0.08 | Lighter hover on dark |
| `--color-text` | 0.96 | Near white |
| `--color-text-muted` | 0.78 | Dim but AA-passing |
| `--color-text-inverse` | same as dark bg | On primary bg |
| `--color-background` | 0.10 | Deep dark, seed-hue-tinted |
| `--color-surface` | 0.14 | Slightly lighter panel |
| `--color-surface-raised` | 0.19 | Elevated surface |

## Semantic state colors

Hue offsets from the seed (used for success/warning/danger/info):

| Role | Light L | Dark L | Hue shift |
|---|---|---|---|
| `--color-success` | 0.40 | 0.72 | seed-hue shifted to 145° (green) |
| `--color-warning` | 0.40 | 0.72 | seed-hue shifted to 75° (amber) |
| `--color-danger` | 0.40 | 0.72 | seed-hue shifted to 25° (red) |
| `--color-info` | same as primary | same | no shift |

State colors blend toward their target hue over 70% weight, preserving 30% of the seed hue to maintain palette cohesion.

## Chroma clamping

After OKLCH manipulation, convert back to sRGB and clamp channels to [0, 1]. If clamping changes any channel by >0.02, reduce chroma (C) in steps of 0.01 until the result is fully within gamut. This avoids blown-out colors while preserving hue and lightness.

## Output format

The script outputs JSON to stdout:

```json
{
  "seed": "#4f46e5",
  "modes": {
    "light": {
      "--color-background": "#ffffff",
      "--color-surface": "#f8f8ff",
      ...
    },
    "dark": {
      "--color-background": "#0c0b1a",
      ...
    }
  },
  "reasons": []
}
```

On failure (e.g. seed cannot be shifted to a gamut-safe AA-passing primary), exits 1 with a non-empty `"reasons"` array explaining which pairs failed and why.
