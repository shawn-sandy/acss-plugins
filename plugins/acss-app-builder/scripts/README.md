# acss-app-builder scripts

Python helpers invoked by the plugin's slash commands. All scripts are Python 3 stdlib only — no external dependencies.

The four scripts split into two groups with different output contracts:

- **Detection scripts** (`detect_vite_project.py`, `detect_component_source.py`) — print a single JSON object on stdout.
- **Validator scripts** (`validate_css_vars.py`, `validate_theme.py`) — print human-readable plain text on stdout; signal result via exit code.

Each script carries a full usage docstring at the top of the file. This README indexes them so you can pick the right one without opening all four.

## Index

| Script | Purpose | Primary input | Stdout | Exit codes |
|---|---|---|---|---|
| [`detect_vite_project.py`](./detect_vite_project.py) | Detect a Vite + React project and locate its entry file. TypeScript is reported as metadata but is not required for detection. | `[project_root]` (defaults to cwd) | JSON object | `0` = Vite + React detected, `1` = not detected |
| [`detect_component_source.py`](./detect_component_source.py) | Decide whether to import fpkit components from generated source, the `@fpkit/acss` npm package, or neither | `[project_root]` (defaults to cwd) | JSON object | `0` = `generated` or `npm` resolved, `1` = no project root found or `source=none` |
| [`validate_css_vars.py`](./validate_css_vars.py) | Validate CSS custom properties in SCSS files against fpkit naming conventions (`--{component}-{property}`, rem units, approved abbreviations) | `[file_or_directory]` (defaults to cwd) | Plain text summary + per-file error listing | `0` = all valid (or no SCSS files found), `1` = at least one violation |
| [`validate_theme.py`](./validate_theme.py) | Validate a theme CSS file (`light.css`, `dark.css`, `brand-*.css`) for WCAG AA contrast on semantic role pairs | `<file-or-dir>` | Plain text summary + per-failure listing | `0` = no failures, `1` = contrast pair below threshold, `2` = usage / IO error |

## Detection script output

Both detection scripts print a single JSON object to stdout.

```jsonc
// detect_vite_project.py
{
  "isVite": true,
  "isReact": true,
  "isTypeScript": true,
  "projectRoot": "/abs/path",
  "entry": "src/main.tsx",
  "viteConfig": "vite.config.ts",
  "reasons": ["..."]          // populated on failure paths; may be empty on success
}

// detect_component_source.py — success path
{
  "source": "generated",      // or "npm" or "none"
  "projectRoot": "/abs/path",
  "componentsDir": "src/components/fpkit",
  "importMapHint": "import Button from '../src/components/fpkit/button/button'"
}

// detect_component_source.py — no-project-found error path (exit 1)
{
  "source": "none",
  "projectRoot": null,
  "componentsDir": "src/components/fpkit",
  "importMapHint": "",
  "reasons": ["No project root containing react was found."]
}
```

Note: `detect_component_source.py` emits `importMapHint` on the success path and `reasons` only on the no-project-found error path. Consumers should branch on the `source` field.

## Validator script output

Validators print plain text designed for a human reader, not JSON. Downstream consumers should treat the **exit code** as the authoritative signal and the stdout as diagnostic detail.

```
# validate_css_vars.py (success)
Validating 12 file(s)...

✓ All CSS variables are valid!

# validate_css_vars.py (failure)
✗ Found 3 validation error(s):

styles/button.scss:
  Line 14: --btn-background-color
    Use approved abbreviation 'bg' instead of 'background-color'

# validate_theme.py (success)
validate_theme: OK (2 palette file(s) checked)

# validate_theme.py (failure)
Contrast failures:
  light.css: color-text on color-bg = 3.12:1 (required 4.5:1) [resolved fg=#888, bg=#fff]
```

## Running a script directly

```bash
python3 plugins/acss-app-builder/scripts/detect_vite_project.py /path/to/project
python3 plugins/acss-app-builder/scripts/validate_theme.py src/styles/light.css
```

Inside Claude Code, these are invoked automatically by the plugin's skills — you generally don't need to run them by hand.
