---
paths:
  - "plugins/acss-app-builder/scripts/**"
---

# Python Script Inventory

Current scripts in `plugins/acss-app-builder/scripts/`:

- `detect_vite_project.py` — detects whether the target directory is a Vite project
- `detect_component_source.py` — locates fpkit component source files in the project tree
- `validate_css_vars.py` — validates SCSS CSS custom properties against fpkit naming conventions and unit rules
- `validate_theme.py` — checks theme CSS files (light/dark/brand) for WCAG AA contrast on semantic role pairs
