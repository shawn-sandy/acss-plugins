---
description: Generate an accessible React form from a JSON field schema
argument-hint: <schema.json> [--name=FormName] [--force]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
---

Generate `src/forms/<FormName>.tsx` from a JSON field schema.

Follow the `/app-form` section of `.claude/plugins/acss-app-builder/skills/acss-app-builder/SKILL.md` and the verified Field API in `references/forms.md`.

**Supported field types:** `text`, `email`, `password`, `url`, `number`, `tel`, `date`, `select`, `textarea`, `checkbox`, `radio`.

**Example schema:** `assets/forms/schema.example.json`.

**Quick steps:**

1. Shared preflight.
2. Read and validate the schema (`name`, `fields[].{name,label,type}` required).
3. Read `assets/forms/form-from-schema.tsx.tmpl`.
4. Render each field using the type→renderer mapping. Generate unique ids `<FormName>-<fieldName>`.
5. Substitute `{{IMPORT_SOURCE:Field,Input,Checkbox,Button}}`.
6. Write to `src/forms/<FormName>.tsx` (refuse non-empty without `--force`).
7. Print a usage snippet.

**Important:** The fpkit package exports `Field`, `Input`, `Checkbox` — NOT `FieldLabel`, `FieldInput`, `Select`, or `Textarea`. Native `<select>` and `<textarea>` are used inside `<Field>`.
