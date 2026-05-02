# `.agents/`

Mirror of selected project skills exposed to **GitHub Managed Agents** (Copilot-style coding agents that run from CI without a Claude Code IDE session). The Managed Agents runtime discovers skills under `.agents/skills/`, not `.claude/skills/` — hence the duplication.

## What's here

| Skill | Mirrors | Purpose |
|---|---|---|
| `add-command` | `.claude/skills/add-command/` | Scaffold a new slash command in a plugin |
| `release-check` | `.claude/skills/release-check/` | Audit version-bump + CHANGELOG + README before opening a release PR |
| `release-plugin` | `.claude/skills/release-plugin/` | Bump `plugin.json` version and refresh `marketplace.json` description |
| `validate-plugin` | `.claude/skills/validate-plugin/` | Single-plugin structural validation |
| `verify-plugins` | `.claude/skills/verify-plugins/` | Cross-plugin structural validation |

## Drift policy

When you edit one of the canonical skills under `.claude/skills/<name>/SKILL.md`, the matching `.agents/skills/<name>/SKILL.md` should be updated in the same commit. The two copies diverge only when a skill needs runtime-specific guidance (Managed Agents has no interactive prompts; Claude Code does). If a divergence is intentional, note it inline in the `.agents/` copy.

## When to remove this directory

If GitHub Managed Agents is no longer used against this repo, `.agents/` can be deleted entirely — `.claude/skills/` covers every interactive Claude Code session.
