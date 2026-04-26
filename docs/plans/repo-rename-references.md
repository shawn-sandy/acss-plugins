# Update repo references for `shawn-sandy/acss-plugins` → `shawn-sandy/agentic-acss-plugins`

## Context

The GitHub repository was renamed from `shawn-sandy/acss-plugins` to `shawn-sandy/agentic-acss-plugins`. The git remote in this worktree already points at the new URL (`origin → https://github.com/shawn-sandy/agentic-acss-plugins.git`), but in-repo install instructions, marketplace metadata, and prose still reference the old slug. Users following any current install command would have to rely on GitHub's redirect, which is brittle for the Claude Code marketplace resolver.

Claude Code derives the install suffix from `<owner>-<repo>`, so it changes from `@shawn-sandy-acss-plugins` → `@shawn-sandy-agentic-acss-plugins`.

## Objective

Refresh every in-repo reference to the marketplace path so the README/install snippets, marketplace manifest, contributor docs, and migration notes all point to the new repo. No plugin behavior changes.

## Steps

1. **Marketplace manifest** — `.claude-plugin/marketplace.json`
   - `"name": "acss-plugins"` → `"name": "agentic-acss-plugins"` (line 3)
   - `"owner.url"` → `https://github.com/shawn-sandy/agentic-acss-plugins` (line 7)

2. **Root README** — `README.md`
   - Title `# acss-plugins` → `# agentic-acss-plugins` (line 1)
   - Install snippet `marketplace add` and `install` lines (lines 14–15)

3. **CLAUDE.md** (lines 18–19)
   - Update both install lines.

4. **GUIDE.md** (lines 13–14, 113–117)
   - Install snippet (lines 13–14)
   - Migration uninstall/install block — 4 plugins each carrying the `@shawn-sandy-acss-plugins` suffix (lines 113–117)
   - Description prose at line 4 mentioning `acss-plugins`

5. **AGENTS.md** (lines 19–20, 81)
   - Install snippet
   - Local-path fallback example mentioning the absolute path

6. **Plugin README** — `plugins/acss-kit/README.md` (lines 43, 60–61)
   - All install snippets

7. **Plugin CHANGELOG** — `plugins/acss-kit/CHANGELOG.md`
   - Update the install command at line 57 inside the v0.3.0 migration block (still actionable today — broken commands here would mislead users mid-migration)
   - Add an `[Unreleased]` entry: `- Marketplace repo renamed from \`shawn-sandy/acss-plugins\` to \`shawn-sandy/agentic-acss-plugins\`. Install commands now use \`@shawn-sandy-agentic-acss-plugins\`.`

8. **Plugin tutorial** — `plugins/acss-kit/docs/tutorial.md` (line 15)
   - Install snippet

9. **CONTRIBUTING.md** (line 77)
   - Prose reference `shawn-sandy/acss-plugins` → new slug

10. **Test harness package**
    - `tests/package.json`: `name` (`acss-plugins-tests` → `agentic-acss-plugins-tests`) and the description string
    - `tests/package-lock.json`: regenerate after the package.json edit via `npm --prefix tests install --package-lock-only` so the lock's `name` and root `packages.""` entries stay consistent
    - `tests/run.sh` line 2: update header comment if it references the repo name
    - `tests/README.md` lines 136, 139, 185, 193: install/marketplace snippets

11. **Plan archive prose** — `docs/plans/document-claude-maintainer-tooling.md` (line 5)
    - Update current-state prose that names the repo (the file describes ongoing tooling, not a frozen snapshot)
    - In `docs/plans/test-docs-harness-alignment.md`, **leave the commit URL** at line 5 unchanged — the commit SHA is immutable and GitHub redirects renamed-repo commit URLs reliably.

12. **Maintainer review agents** — `.claude/agents/README.md` and `.claude/agents/{component-reference,python-script,skill-quality,theme-reference}-reviewer.md`
    - Each agent system prompt opens with "You are a {role} for the acss-plugins repo[sitory]" — update the repo name. Five files, one occurrence each.
    - **Found late** because this worktree lives at `.claude/worktrees/<name>/` inside the parent checkout, and the parent repo's `.gitignore` has `.claude/worktrees/`. Default ripgrep walks up to the parent gitignore and applies its rules — so it skipped these tracked-but-superficially-ignored files. Run verification grep with `--no-ignore` (or scope to the worktree's `.claude/`) to avoid the trap.

## Critical files

- `.claude-plugin/marketplace.json` — marketplace identifier, user-visible
- `README.md`, `plugins/acss-kit/README.md`, `GUIDE.md` — primary install entry points
- `plugins/acss-kit/CHANGELOG.md` — referenced by users following the migration path
- `tests/package.json` + `tests/package-lock.json` — must move together to keep `npm --prefix tests ci` deterministic

## Out of scope

- **Sibling repo `shawn-sandy/acss`** — that's the separate fpkit library and is unaffected by this rename
- **No plugin version bump for `acss-kit`** — see "Alternative considered" below
- **Git remote** — already updated by the user
- **Historical CHANGELOG version headers and prose body** — only the embedded install snippet in the v0.3.0 migration block is touched; dated entries are not rewritten
- **Plan-archive commit URL** — preserved as a stable historical reference

## Alternative considered

Bump `plugins/acss-kit/.claude-plugin/plugin.json` (e.g. patch bump for the rename). **Rejected** because the plugin contract — commands, skills, components, generated CSS — is byte-identical. `/plugin update` would pull no functional change. The pre-submit checklist's version-bump rule exists for behavioral changes; a marketplace path rename is documented in CHANGELOG `[Unreleased]` and ships with the next real release.

## Verification

After edits, run from the repo root:

```sh
# 1. No remaining references to the old slug or old install suffix.
#    Use --no-ignore because this worktree lives under the parent's
#    ignored .claude/worktrees/ path and ripgrep would otherwise skip it.
rg --pcre2 --no-ignore '(?<!agentic-)acss-plugins' -g '!.git' -g '!node_modules' -g '!tests/node_modules'
# Expected: only the preserved commit URL in docs/plans/test-docs-harness-alignment.md,
# the [Unreleased] CHANGELOG entry that documents the rename, and this plan file itself.

# 2. marketplace.json is still valid JSON
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null

# 3. Plugin manifest is untouched (no accidental version bump)
git diff plugins/acss-kit/.claude-plugin/plugin.json
# Expected: empty

# 4. Lockfile and package.json agree
node -e "const a=require('./tests/package.json').name, b=require('./tests/package-lock.json').name; if(a!==b) {console.error('mismatch', a, b); process.exit(1)}"

# 5. Structural test pass
tests/run.sh
```

End-to-end smoke (optional, requires a fresh Claude Code session): run `/plugin marketplace add shawn-sandy/agentic-acss-plugins` then `/plugin install acss-kit@shawn-sandy-agentic-acss-plugins` and confirm the new identifier resolves and `/kit-add button` still works.

## Next Steps

- After merge: open a follow-up PR that bumps `acss-kit` for its next real change and folds the `[Unreleased]` rename note into the release entry.
