---
description: Validate component specs against the schema; optionally flag stale project stamps
argument-hint: [<component>] [--stale]
allowed-tools: Bash, Read
---

Validates one or all specs and reports errors.

1. Run `python scripts/validate_spec.py [specs/<component>.md] [--stale]`.
2. Without a component argument, validates all `specs/*.md`.
3. Reports schema errors, missing a11y blocks, invalid WCAG SCs, and format_version mismatches.
4. `--stale`: scans project component files for `// generated from` stamps with versions older than the current spec; reports each stale file.

Exit 0 = all specs valid. Exit 1 = one or more validation errors (details in JSON output).

Follow SKILL.md § /spec-validate.
