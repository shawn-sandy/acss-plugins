---
description: Render a component spec into framework-specific files in staging
argument-hint: <component> [--target=react|html|astro|all]
allowed-tools: Read, Write, Edit, Bash, Glob
---

Renders `specs/<component>.md` into `<project>/.acss-staging/<framework>/`.

1. Run `python scripts/plan_render.py <component> [--target=<target>]` to get the dependency tree and file manifest.
2. Default target resolution:
   - Read `.acss-target.json`; if `framework` field is set, use it.
   - If unset, render all three frameworks.
3. Read `references/frameworks/<target>.md` for the renderer strategy.
4. Emit files bottom-up per the dependency tree (leaf components before composites).
5. Render atomically: if any framework fails, halt all and report. Never leave partial staging output.
6. Stamp each generated file: `// generated from <component>.md@<version>`.
7. Warn if no `acss-theme-builder` output is detected: "no theme detected; relying on hardcoded fallbacks."
8. On first invocation, auto-add `.acss-staging/` to project `.gitignore` (prompt user to confirm).

Follow SKILL.md § /spec-render for the canonical 3-step render flow.
