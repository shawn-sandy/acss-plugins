# Project Rules

Advisory text auto-loaded into Claude's context whenever it touches a file matching the rule's `paths:` glob. Unlike [hooks](../hooks.md), rules **do not block or warn** — they're just reminders that ride along in the prompt.

| Rule | Triggers on | Status |
|---|---|---|
| [`scss-conventions.md`](scss-conventions.md) | `**/*.scss`, `**/*.css` | Active — variable naming pattern, `var()` fallbacks, `[aria-disabled="true"]` for disabled state. |
| [`python-scripts.md`](python-scripts.md) | `plugins/acss-app-builder/scripts/**` | **Drift** — references `acss-app-builder`, a predecessor plugin consolidated into `acss-kit` at v0.3.0. The path glob never matches a real file, so this rule never loads. Fix: rewrite the inventory for `plugins/acss-kit/scripts/**`, or delete the file. |

## Rules vs. hooks vs. skills

| Layer | Purpose | Where it lives | When it runs |
|---|---|---|---|
| Rule | Inject advisory context | `.claude/rules/<name>.md` with `paths:` front-matter | When Claude reads/writes a matching file |
| [Hook](../hooks.md) | Validate or block tool calls | `.claude/settings.json` `hooks` block | Before/after a tool call |
| [Skill](../skills/README.md) | Author or update artifacts | `.claude/skills/<name>/SKILL.md` | When Claude routes a request to it (or the maintainer slashes it) |

Use **rules** to reinforce a convention you want present every time (naming, security boundaries). Use **hooks** to actually enforce or warn. Use **skills** for multi-step workflows.

## Adding a new rule

1. Create `.claude/rules/<rule-name>.md`.
2. Front-matter must include a `paths:` array of glob patterns.
3. Body is the advisory text — keep it short; it's loaded on every match.
4. Add a row to the table above.
