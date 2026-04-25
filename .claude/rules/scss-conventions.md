---
paths:
  - "**/*.scss"
  - "**/*.css"
---

# SCSS / CSS Variable Conventions

- Pattern: `--{component}-{element?}-{variant?}-{property}`
- Every `var()` must include a hardcoded fallback: `var(--btn-bg, transparent)`
- Disabled state: `[aria-disabled="true"]` selector — never the native `disabled` attribute
