# Document the local maintainer tooling under `.claude/`

## Context

The `acss-plugins` repo ships one plugin (`acss-kit`) but holds substantial **maintainer-only tooling** at the repo-root `.claude/` directory: 4 review agents, 4 review commands, 10 authoring/release skills, 2 rules files, and a `settings.json` enforcing 6 hooks (4 PostToolUse + 2 PreToolUse). Only the agents are documented (`.claude/agents/README.md`). The rest is undocumented, so a contributor (or returning maintainer) browsing `.claude/skills/` cannot tell that `/release-plugin`, `/component-author`, `/plugin-health`, etc. exist or when to use them.

Goal: make the `.claude/` directory self-documenting so a developer landing in the repo can quickly run the right tool. Mirror the existing per-category README pattern (`agents/README.md`) rather than consolidating into a single file — depth-per-category × 16 items would produce a 500-line index, and contributors editing `.claude/skills/` look for a sibling README, not one a level up.

## Objective

Add a contributor-facing index plus per-category READMEs under `.claude/`, link to them from `CONTRIBUTING.md` and `AGENTS.md`, and document the `settings.json` hooks (including the one dead reference). No source-code changes.

## Critical files

**To create (5):**
- `.claude/README.md` — top-level index ("I want to..." task table, links to category READMEs and `hooks.md`)
- `.claude/skills/README.md` — table of 10 skills (name, one-line description, trigger phrase / slash command if any)
- `.claude/commands.md` — table of 4 review commands (command, description, agent dispatched). Lives one level above `commands/` because the slash-command loader treats every `.md` in `commands/` as a command (even without front-matter) — a `commands/README.md` would have registered as `/README`. Discovered during implementation.
- `.claude/rules/README.md` — table of 2 rules (filename, what it governs, who reads it)
- `.claude/hooks.md` — what `settings.json` enforces; `settings.json` vs `settings.local.json`; flag the dead `acss-component-specs` parity hook

**To edit (2):**
- `CONTRIBUTING.md` — add ~5-line "Maintainer tooling" subsection linking `.claude/README.md`
- `AGENTS.md` — one-line pointer to `.claude/README.md` in the existing "What this repo is" block

**To read while authoring (no edits):**
- `.claude/agents/README.md` — canonical README pattern to mirror
- `.claude/skills/<each>/SKILL.md` — pull `description` from front-matter for the skills table
- `.claude/commands/<each>.md` — pull `description` and `argument-hint` for the commands table
- `.claude/rules/python-scripts.md`, `.claude/rules/scss-conventions.md` — confirm scope of each rule
- `.claude/settings.json` — source for `hooks.md`

## Steps

1. **Read source-of-truth front-matter for the skills table.** Open all 10 `.claude/skills/<name>/SKILL.md` files and pull the `description:` field. Why: the README must match what Claude actually loads, not a re-paraphrase.

2. **Read source-of-truth front-matter for the commands table.** Open all 4 `.claude/commands/<name>.md` files and pull `description:` and `argument-hint:`. Why: same reason — the README is a derived view, not a fresh authoring of intent.

3. **Write `.claude/skills/README.md`.** Single table: skill name | description | how to invoke (slash command if one exists; otherwise "Claude auto-invokes when ..."). Group rows by purpose (Authoring / Updating / Validation / Release) for scannability. Why: 10 alphabetical rows are noise; 4 grouped clusters of 2-3 rows are scannable.

4. **Write `.claude/commands.md`.** Single table: command | description | dispatches to (agent name from `.claude/agents/README.md`). Add a one-line note that all four commands wrap an agent and write nothing. Why: contributors should know these are review-only before running them. Note: this file lives at `.claude/commands.md` (one level above `commands/`), not `.claude/commands/README.md` — the slash-command loader registers every `.md` inside `commands/` as a command, so the doc would have leaked through as `/README`.

5. **Write `.claude/rules/README.md`.** Two-row table: rule file | scope | when Claude reads it. Add a note that rules are advisory text loaded into Claude's context for matching files, not enforced hooks. Why: the distinction between rules (advisory) and hooks (enforced) is non-obvious and easy to confuse.

6. **Write `.claude/hooks.md`.** Document each of the 6 hooks: matcher, what it does, exit behaviour, statusMessage. Group as "PostToolUse" (4 advisory) and "PreToolUse" (2 blocking). Add a "Files" section explaining `settings.json` (committed, hooks live here) vs `settings.local.json` (machine-local, permissions allowlist). Add a "Known drift" callout: the spec/kit-builder parity hook references `plugins/acss-component-specs/` and `plugins/acss-kit-builder/`, neither of which exist post-v0.3.0 consolidation — the hook will never fire. Why: contributors deserve an honest map of what's enforced; pretending the dead hook works is misleading.

7. **Write `.claude/README.md`.** Sections: header ("Maintainer tooling for working on acss-kit"); "I want to..." task table (rows for: add a component, update a component, add a brand preset, update a theme, run pre-PR validation, bump a plugin version, audit a SKILL.md, audit a Python script, add a slash command); links to each category README; pointer to `.claude/agents/README.md` (already canonical); pointer to `.claude/hooks.md`. Keep under 80 lines. Why: the top-level index must stay scannable; deep info lives in category files.

8. **Edit `CONTRIBUTING.md`.** Add a new subsection after "Repo structure" titled "Maintainer tooling" with 4-5 lines: one sentence explaining the `.claude/` directory contains review agents, authoring skills, validation commands, and release helpers; a link to `.claude/README.md`. Why: `CONTRIBUTING.md` is the human contributor entry point; without a link they may never find `.claude/README.md`.

9. **Edit `AGENTS.md`.** Add one bullet to the existing "What this repo is" section: `Maintainer tooling for working on this repo lives at `.claude/` — see [.claude/README.md](.claude/README.md).` Why: `AGENTS.md` is the coding-agent entry point; the same link belongs there because Claude itself benefits from finding the index.

10. **Run the pre-submit checklist.** Execute `tests/run.sh` to confirm no structural validation regresses. Why: `CONTRIBUTING.md` is one of the files validated; an inadvertent broken link or front-matter would surface here.

## Verification

- `cat .claude/README.md` renders as a scannable index, all internal links resolve to files in this commit
- `ls .claude/README.md .claude/skills/README.md .claude/rules/README.md .claude/commands.md .claude/hooks.md` shows all 5 new doc files present
- For each catalog, the count matches what's on disk: `.claude/skills/README.md` has 10 rows, `.claude/commands.md` has 4 rows, `.claude/rules/README.md` has 2 rows
- Open the 5 new files locally and confirm every cross-link path is repo-relative (no `file://`, no absolute paths)
- `tests/run.sh` exits 0
- `git diff --stat` shows exactly 5 new files + 2 edited files (`CONTRIBUTING.md`, `AGENTS.md`); no other changes
- Manually click through from `CONTRIBUTING.md` → `.claude/README.md` → each category README on GitHub once the PR is open, confirming GitHub auto-renders each `README.md` when navigating into the directory

## Next Steps (out of scope)

- **Fix the dead parity hook in `settings.json`** — references gone-since-v0.3.0 plugins. Either delete it or rewrite it for `acss-kit`. Worth a separate PR with its own decision (delete vs port).
- **Fix stale paths in `settings.local.json` allowlist** — references `plugins/acss-app-builder/assets/themes/`. Personal/machine-local file, low priority, but worth pruning.
- **Reconcile `AGENTS.md` ↔ `CLAUDE.md` overlap** — both files restate the same repo overview. Either consolidate into one canonical source with a stub in the other, or leave the duplication as a deliberate choice for the two audiences. Out of scope for documentation work; raise as a separate question.
- **Inline per-skill docs in `.claude/skills/README.md`** — currently only one-line descriptions; could grow into per-skill sections like `.claude/agents/README.md` does (checks tables, sample output). Defer until contributors actually ask for that depth.

## Unresolved Questions

- Should `.claude/README.md` group skills by **purpose** (Authoring / Updating / Validation / Release) or alphabetically? The plan above proposes by-purpose; alphabetical is easier to author but harder to scan.
- Should `CONTRIBUTING.md`'s new subsection be under "Repo structure" (current proposal) or after "Testing locally"? Either is defensible.
