---
description: Regenerate token-bridge.css against the active acss-kit theme (with mandatory dark-mode parity)
argument-hint: [--theme=<file>]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Regenerate `token-bridge.css` so the fpkit-style aliases (`--color-error`, `--color-error-bg`, `--color-primary-light`, …) resolve to the user's active acss-kit theme. Always emits both `:root` and `[data-theme="dark"]` blocks.

Follow the `/utility-bridge` section of `${CLAUDE_PLUGIN_ROOT}/skills/utilities/SKILL.md`.

**Arguments:**

- `--theme=<file>` — override the source theme. Otherwise the command auto-detects `src/styles/theme/light.css` and `dark.css` in the project root.

**Quick steps:**

1. Resolve the source theme(s). On no-find, fall back to the bundled defaults at `${CLAUDE_PLUGIN_ROOT}/assets/token-bridge.css` and warn the user.
2. Extract `--color-danger`, `--color-primary`, `--color-success`, `--color-warning`, `--color-info` for both light and dark modes.
3. Build the bridge with `var()` chains and embedded hex fallbacks. Synthesize `-bg` and `-light` variants via `color-mix(in oklch, …)`.
4. Write the file to `<projectRoot>/<utilitiesDir>/token-bridge.css` (default `src/styles/token-bridge.css`).
5. Run `scripts/validate_utilities.py <bridge-file>` to enforce dark-mode parity.
6. Print a summary: which roles were aliased, dark-mode parity status, fallback values used.
