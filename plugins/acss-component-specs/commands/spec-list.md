---
description: List all available component specs and their render status
argument-hint: [<component>]
allowed-tools: Read, Bash, Glob
---

Lists specs and their render status.

1. Glob `specs/*.md` to find all spec files.
2. For each spec, read `name`, `format_version`, and `fpkit_version` from frontmatter.
3. If a component name is given, show that spec's full summary including props and css_vars.
4. If `specs/` is empty or missing, output:
   ```
   No specs found. Run /spec-add <component> to scaffold your first spec.
   Install hint: /plugin install acss-component-specs@acss-plugins
   ```

Follow SKILL.md § /spec-list.
