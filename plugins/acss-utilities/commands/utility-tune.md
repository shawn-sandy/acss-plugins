---
description: Adjust the utility-class tokens (spacing baseline, breakpoints, family enables) via natural language
argument-hint: <natural-language description>
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Adjust `utilities.tokens.json` based on a natural-language request, regenerate the bundle, and validate the result.

Follow the `/utility-tune` section of `${CLAUDE_PLUGIN_ROOT}/skills/utilities/SKILL.md`.

**Examples:**

```
/utility-tune use a 4px spacing baseline
/utility-tune use an 8px spacing baseline
/utility-tune add an xs breakpoint at 20rem
/utility-tune disable shadow utilities
/utility-tune drop responsive variants from spacing
/utility-tune add a 'soft' radius value at 1rem
```

**Quick steps:**

1. Parse the prompt into one or more concrete edits to `utilities.tokens.json`. If ambiguous, use `AskUserQuestion` to clarify before writing.
2. Read `${CLAUDE_PLUGIN_ROOT}/assets/utilities.tokens.json`. Apply edits.
3. Write the updated tokens back to disk (preserve key order).
4. Run `scripts/generate_utilities.py --tokens <file> --out-dir ${CLAUDE_PLUGIN_ROOT}/assets/`.
5. Run `scripts/validate_utilities.py ${CLAUDE_PLUGIN_ROOT}/assets/`.
   - On `ok: false`: print reasons, **revert the tokens edit**, halt. The committed bundle should never go out of contract.
6. Print a summary: which tokens fields changed, new bundle size, classes added/removed.
