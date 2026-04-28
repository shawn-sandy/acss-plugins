---
description: Adjust visual feel of theme roles or component tokens using natural language
argument-hint: <natural-language description>
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

Tune acss-kit components or theme roles by describing how they should
feel — softer, warmer, calmer, more spacious, more elevated, smaller,
narrower. The skill routes between theme-role edits (delegated to
`/theme-update` with WCAG pre-validation) and component SCSS token
edits.

Follow the workflow in `${CLAUDE_PLUGIN_ROOT}/skills/style-tune/SKILL.md`.

**Arguments:**

- `<natural-language description>` — one or more sentences naming a
  component (button, card, alert, dialog, input, nav) or theme role
  (primary, accent, danger, warning, info, success, brand) plus a
  modifier from the intent vocabulary (softer, warmer, spacious,
  elevated, smaller, etc.).

**Quick steps:**

1. Resolve the subject and modifiers; route to the theme or component
   layer (Step A).
2. Locate the in-scope theme files or component SCSS file (Step B).
3. Compute deltas — for color modifiers call
   `scripts/oklch_shift.py`; for radius/spacing/size apply the
   canonical multiplier from `references/intent-vocabulary.md`
   (Step C).
4. **Theme batch:** stage edits, pre-validate via
   `scripts/validate_theme.py`, halt the entire batch on any
   contrast failure. **Component batch:** edit the SCSS atomically
   in memory, preserving all `var()` wrappers (Step D).
5. Validate structurally and surface drift hints when applicable
   (Step E).
6. Print a Modifier / Token / Old / New / Status table plus next-step
   hints (Step F).

**Example prompts:**

- "Make the button feel softer and warmer."
- "Tone down the primary color a touch."
- "Give the alert a calmer look."
- "More spacious cards."
- "Style the dialog to feel more elevated."
- "Narrower dialog."
- "Smaller buttons."

**Auto-trigger:** these phrases also route to `style-tune` directly
without needing the slash command — see the SKILL.md front-matter
description for the full trigger surface.
