# Maintainer tooling

Project-local Claude Code definitions for working on the `acss-kit` plugin. Contributors use these to scaffold new artifacts, audit existing ones, and gate releases. End-user docs for the plugin itself live at [GUIDE.md](../GUIDE.md), the [root README](../README.md), and [plugins/acss-kit/README.md](../plugins/acss-kit/README.md).

## I want to...

| Task | Tool |
|---|---|
| Add a new component reference | `/component-author <name>` |
| Update an existing component reference | `/component-update <name>` |
| Add a brand preset, palette role, or schema field | `/style-author` |
| Update a theme reference, then re-validate | `/style-update <path>` |
| Bump the plugin version before committing | `/release-plugin <plugin> <version>` |
| Audit release paperwork before opening a PR | `/release-check <plugin>` |
| One-shot health audit on the plugin | `/plugin-health` |
| Validate a single plugin's structure | `/validate-plugin <name>` |
| Audit every plugin in the repo | `/verify-plugins` |
| Audit a SKILL.md or command file for shape | ask Claude — routes to [`skill-quality-reviewer`](agents/README.md#skill-quality-reviewer) |
| Audit a single Python script | `/review-script <path>` |
| Audit every Python script in parallel | `/review-scripts` |
| Audit a component reference doc | `/review-component <path>` |
| Audit theme cross-source parity | `/review-themes` |
| Add a new slash command to a plugin | `/add-command <plugin> <command>` |

## Catalogs

| Category | Count | Reference |
|---|---|---|
| Skills | 10 | [skills/README.md](skills/README.md) |
| Commands | 4 | [commands.md](commands.md) |
| Agents | 4 | [agents/README.md](agents/README.md) |
| Rules | 2 | [rules/README.md](rules/README.md) |
| Hooks | 6 | [hooks.md](hooks.md) |

## Layout

```
.claude/
├── README.md            # this file — index
├── commands.md          # slash-command catalog (lives here, not in commands/, to avoid the loader)
├── hooks.md             # settings.json hook reference
├── settings.json        # hooks (committed)
├── settings.local.json  # personal permissions allowlist (gitignored)
├── agents/<name>.md     # review-only sub-agents (+ agents/README.md catalog)
├── commands/<name>.md   # slash command files
├── rules/<name>.md      # advisory text injected by path glob
└── skills/<name>/SKILL.md  # multi-step authoring/release workflows
```

## Adding a new tool

- **Skill** — `mkdir .claude/skills/<name>/`, then write `SKILL.md` per [skills/README.md](skills/README.md).
- **Command** — write `.claude/commands/<name>.md` with `description:` and `allowed-tools:` front-matter; see [commands.md](commands.md).
- **Agent** — see "Adding a new agent" in [agents/README.md](agents/README.md).
- **Rule** — see [rules/README.md](rules/README.md).
- **Hook** — edit `.claude/settings.json` and document in [hooks.md](hooks.md).

## See also

- [CONTRIBUTING.md](../CONTRIBUTING.md) — sibling-clone workflow, pre-PR checklist
- [AGENTS.md](../AGENTS.md) — coding-agent guidance for working in this repo
- [GUIDE.md](../GUIDE.md) — end-user guide for the `acss-kit` plugin
