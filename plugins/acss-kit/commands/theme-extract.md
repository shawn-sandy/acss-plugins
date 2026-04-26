---
description: Extract theme tokens from an image or Figma URL and generate theme CSS
argument-hint: <image-path|figma-url>
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Extract brand colors from an image or Figma design and generate theme CSS files.

Follow the `/theme-extract` section of `${CLAUDE_PLUGIN_ROOT}/skills/styles/SKILL.md`.

**Arguments:**

- `<image-path>` — local image file path (PNG, JPG, WebP)
- `<figma-url>` — `figma.com/design/...` URL

**Quick steps:**

1. Detect input type: Figma URL → invoke `figma-design-tokens` skill; image path → invoke `design-token-extractor` skill.
2. Both extractors return a JSON object with at minimum a `primary` hex color. Map to `--color-primary` in the seed.
3. Run `scripts/generate_palette.py <primary-hex> --mode=both` to build the full palette around the extracted primary.
4. Run `scripts/tokens_to_css.py` to write theme files. Validate with `scripts/validate_theme.py`.
5. The CSS theme files (`light.css`, `dark.css`, `brand-*.css`) are the authoritative output. JSON export via `scripts/css_to_tokens.py` is available for round-trip tooling, but is not a user-facing input format — see the CSS Token Convention in SKILL.md for the canonical authoring approach.
