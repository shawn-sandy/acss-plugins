---
description: Compose or extend fpkit components (successor to the deprecated /fpkit-developer:fpkit-dev command)
argument-hint: <name> [description]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Guided workflow for building a new component from `@fpkit/acss` primitives, or extending one.

Follow the `/app-compose` section of `.claude/plugins/acss-app-builder/skills/acss-app-builder/SKILL.md`.

**This command replaces** the deprecated `/fpkit-developer:fpkit-dev` from the `fpkit-developer` plugin. If that plugin is still installed, uninstall it to avoid duplicate skill activation:

```
/plugin uninstall fpkit-developer@shawn-sandy-acss
```

**Decision tree:**

1. Can the requirement be met by an existing fpkit export with CSS variable customization? → use it directly.
2. Can it be built by composing 2+ fpkit primitives? → **compose** (≤ 3 levels deep).
3. Can an existing component be wrapped with added behavior? → **extend** (preserve `aria-disabled`, focus, event prevention).
4. Otherwise → **custom** (semantic HTML, rem units, CSS variables per the naming standard).

**Accessibility gate** (applied before finishing):

- Semantic HTML (never `<div role="button">`).
- Keyboard reachable.
- Visible focus.
- WCAG AA color contrast on custom colors.
- Run `scripts/validate_css_vars.py` on any new SCSS.

**Testing:** generated samples use `vitest-axe` (not `jest-axe`) because Vitest is the test runner.
