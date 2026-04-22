# acss-app-builder scripts

Python helpers invoked by the plugin's slash commands. All scripts follow the repo-wide contract documented in [`../../../CLAUDE.md`](../../../CLAUDE.md):

- Python 3 stdlib only — no external dependencies
- Output JSON to stdout
- Exit `0` on success, non-zero on failure
- Include a `"reasons"` array for human-readable error messages

Each script carries a full usage docstring at the top of the file. This README indexes them so you can pick the right one without opening all four.

## Index

| Script | Purpose | Primary input | Exit codes |
|---|---|---|---|
| [`detect_vite_project.py`](./detect_vite_project.py) | Detect a Vite + React + TypeScript project and locate its entry file | `[project_root]` (defaults to cwd) | `0` = detected, `1` = not detected |
| [`detect_component_source.py`](./detect_component_source.py) | Decide whether to import fpkit components from generated source, the `@fpkit/acss` npm package, or neither | `[project_root]` (defaults to cwd) | `0` = resolved, `1` = unresolved |
| [`validate_css_vars.py`](./validate_css_vars.py) | Validate CSS custom properties in SCSS files against fpkit naming conventions (`--{component}-{property}`, rem units, approved abbreviations) | `file_or_directory` | `0` = all valid, non-zero on violations |
| [`validate_theme.py`](./validate_theme.py) | Validate a theme CSS file (`light.css`, `dark.css`, `brand-*.css`) for WCAG AA contrast on semantic role pairs | `<file-or-dir>` | `0` = no failures, `1` = contrast pair below threshold, `2` = usage / IO error |

## Output shape

All scripts print a single JSON object to stdout. Representative fields:

```jsonc
// detect_vite_project.py
{
  "isVite": true,
  "isReact": true,
  "isTypeScript": true,
  "projectRoot": "/abs/path",
  "entry": "src/main.tsx",
  "viteConfig": "vite.config.ts",
  "reasons": ["..."]
}

// detect_component_source.py
{
  "source": "generated" | "npm" | "none",
  "projectRoot": "/abs/path",
  "componentsDir": "src/components/fpkit",
  "reasons": ["..."]
}
```

For validator scripts (`validate_css_vars.py`, `validate_theme.py`), the JSON includes a per-file or per-pair breakdown with pass/fail entries plus a `reasons` array.

## Running a script directly

```bash
python3 plugins/acss-app-builder/scripts/detect_vite_project.py /path/to/project
python3 plugins/acss-app-builder/scripts/validate_theme.py src/styles/light.css
```

Inside Claude Code, these are invoked automatically by the plugin's skills — you generally don't need to run them by hand.
