# Maintainer Skills

Project-local skills for working on the `acss-kit` plugin. These are distinct from the plugin's own end-user skills (which live under `plugins/acss-kit/skills/`) — these run **on this repo while you maintain it**.

Each skill has a slash command of the same name. Claude can also invoke them automatically when the request matches the skill's `description` field.

## Authoring — scaffold new artifacts

| Skill | What it does |
|---|---|
| [`/add-command`](add-command/SKILL.md) | Scaffold a new slash command for a plugin — creates `commands/<name>.md` with front-matter and adds a stub section to the relevant `SKILL.md`. |
| [`/component-author`](component-author/SKILL.md) | Scaffold a new component reference doc under `plugins/acss-kit/skills/components/references/components/<name>.md` in the canonical embedded-markdown shape, and add a placeholder row to the catalog. |
| [`/style-author`](style-author/SKILL.md) | Scaffold a bundled brand preset, palette role, or theme-schema field for `acss-kit`. Three sub-flows; ends with a WCAG 2.2 AA contrast re-validation. |

## Updating — refresh existing artifacts

| Skill | What it does |
|---|---|
| [`/component-update`](component-update/SKILL.md) | Re-verify an existing component reference doc against its captured fpkit ref, surface drift in TSX/SCSS templates, and run the canonical-shape reviewer agent. |
| [`/style-update`](style-update/SKILL.md) | Re-validate and roll forward theme assets after edits to `role-catalogue.md`, `palette-algorithm.md`, `theme.schema.json`, or a bundled brand preset. |

## Validation — read-only audits

| Skill | What it does |
|---|---|
| [`/audit-subagents`](audit-subagents/SKILL.md) | Audit subagent definitions in `.claude/agents/` (and `plugins/*/agents/`) against [Claude Code best practices](https://code.claude.com/docs/en/sub-agents) — front-matter, tool restrictions, description quality, plugin compatibility. Read-only. |
| [`/plugin-health`](plugin-health/SKILL.md) | One-shot audit dashboard for `acss-kit`: structural validation + canonical-shape compliance + catalog parity + bundled theme validation. Read-only. |
| [`/validate-plugin`](validate-plugin/SKILL.md) | Deep per-plugin structural validation (semver, command bodies, fpkit URL hygiene, Python syntax). Run before publishing a specific plugin. |
| [`/verify-plugins`](verify-plugins/SKILL.md) | Repo-wide sweep — pass/fail per plugin with no argument needed. Use to spot-check the marketplace before tagging a release. |

## Release — pre-PR paperwork

| Skill | What it does |
|---|---|
| [`/release-plugin`](release-plugin/SKILL.md) | Bump a plugin's version in `plugin.json` and update `marketplace.json` description if needed. Run **before** committing a publishable change. |
| [`/release-check`](release-check/SKILL.md) | Audit whether release paperwork is complete on the current branch — version bump, CHANGELOG, README all touched as needed. Run **after** `/release-plugin` and **before** opening a PR. |

## Adding a new skill

1. Create `.claude/skills/<skill-name>/SKILL.md` with at minimum a `name:` and `description:` in YAML front-matter.
2. Body is instructions to Claude — explain when to use it and the steps to follow.
3. If the skill should be invokable as a slash command, the folder name is the command name.
4. Add a row to the matching table above.
