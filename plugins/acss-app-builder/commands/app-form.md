---
description: Generate an accessible React form from a natural-language description or legacy JSON field schema
argument-hint: <description-or-schema> [--name=FormName] [--force]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Skill, AskUserQuestion
---

Generate `src/forms/<FormName>.tsx` from a natural-language description (preferred) or a legacy JSON field schema.

This command **delegates to the `acss-kit-builder:component-form` skill** via the Skill tool. The skill owns the form template, field renderers, and accessibility patterns; this command is the user-facing entry point and surfaces the deprecation nudge for projects on the @fpkit/acss npm path.

Follow the `/app-form` section of `.claude/plugins/acss-app-builder/skills/acss-app-builder/SKILL.md` (including the "Cross-plugin skill invocation" subsection) for the full contract.

**Supported field types:** `text`, `email`, `password`, `url`, `number`, `tel`, `date`, `select`, `textarea`, `checkbox`, `radio`.

**Authoring modes:**

- **Natural language** (preferred): `/app-form "signup form with email, password, and a role select"`. The kit-builder skill derives the field list, asking via AskUserQuestion when ambiguous.
- **Legacy JSON** (preserved for backward compatibility): `/app-form path/to/schema.json`. Example schema at `assets/forms/schema.example.json`. The shape is documented in `references/forms.md`.

**Quick steps:**

1. Run shared preflight from SKILL.md (Vite+React detection, component-source detection with deprecation handling).
2. Detect input mode by argument extension: `.json` → legacy schema path; otherwise → natural-language description.
3. If JSON mode: read the schema file, validate required keys (`name`, `fields[].{name,label,type}`), build the structured field list `{ fields, formName, heading?, submitLabel? }`.
4. Invoke the kit-builder skill:
   ```
   Skill {
     skill: "acss-kit-builder:component-form"
     args: <description string>  OR  <structured field-list object>
   }
   ```
5. The skill writes `src/forms/<FormName>.tsx` atomically and prints a summary. Surface that summary directly to the user — don't transform it.
6. If the shared preflight reported `deprecated: true` for the project's component source (i.e. the project is on the @fpkit/acss npm path), append a single-line migration nudge after the summary:

   ```
   Note: this project still uses the @fpkit/acss npm path (deprecated;
   sunset in <sunsetVersion>). Run /kit-add to vendor components.
   ```

**Important:** The fpkit package exports `Field`, `Input`, `Checkbox` — NOT `FieldLabel`, `FieldInput`, `Select`, or `Textarea`. Native `<select>` and `<textarea>` are used inside `<Field>`. The kit-builder skill handles this correctly for both modes; this command does not need to render fields itself.
