# Local Plugin Testing

Two complementary paths: an automated structural validation harness for catching contract regressions on every change, and a manual demo sandbox for exercising slash commands end-to-end.

| Path | Command | When to run | What it catches |
|------|---------|-------------|-----------------|
| Structural validation | `tests/run.sh` | Before every PR; after editing any reference doc | Banned imports, malformed TSX, missing `var()` fallbacks, theme contrast regressions, manifest/structure drift |
| Storybook deep check (optional) | `tests/storybook.sh` | Before merging anything render-sensitive | Live render errors, runtime DOM accessibility violations |
| Demo sandbox | `tests/setup.sh` | When changing slash-command prose; for end-to-end smoke before release | Manual visual confirmation that `/kit-add`, `/theme-create`, etc. produce reasonable output |

## Structural validation: `tests/run.sh`

The default check. ~30 seconds, no browser, single Node devDep.

```sh
# One-time setup
npm --prefix tests ci
pip3 install --user tinycss2

# Every run
tests/run.sh
```

What it does, in order:
1. Wipes `tests/.tmp/`.
2. Extracts TSX/SCSS code blocks from every `plugins/acss-kit/skills/components/references/components/*.md`. Syntax-checks the extracted TSX with TypeScript's parser API. Asserts no banned imports (`@fpkit/acss`).
3. Validates the SCSS contract: every `var(--color-*)`, `var(--font-*)`, `var(--space-*)` reference must include a fallback.
4. Runs the existing WCAG 2.2 AA contrast validator over any `plugins/acss-kit/assets/themes/*.css` (skipped silently if no theme files are present yet).
5. Replicates the `verify-plugins` skill's manifest checks: required `plugin.json` fields, no `version` key in marketplace entries, required files present.
6. Self-tests: runs the validators against `tests/fixtures/known-bad/` and asserts they FAIL. If known-bad starts passing, a validator regex has regressed.

### Serial-only

`tests/run.sh` wipes `tests/.tmp/` at the start of every run. Two concurrent runs in the same checkout will collide. If you need parallel runs, use separate worktrees.

### Why syntax-only TSX validation

The reference docs split TSX across several `## Key Pattern:` and `## Props Interface` sections, with the canonical file living under `## TSX Template`. The extractor pulls only `## Props Interface(s)` and `## TSX Template` — the two sections that match what `/kit-add` writes. Key Pattern sections are intentionally excluded because some contain illustrative JSX (e.g. `<Card><Card.Title>...`) or inline-only snippets (e.g. destructuring `props` outside a function body) that aren't valid at module scope.

A full type-check would require either inlining helpers (fighting the markdown's documentary structure) or accepting non-trivial false negatives. Syntax-level validation via `ts.createSourceFile` catches what regex can't (malformed JSX, broken generics, unclosed strings) without that fight.

### Component Form gap

`skills/component-form/SKILL.md` is **not yet covered** by this harness. The form skill uses richer placeholder substitution (`{{FIELDS}}`) than the simple component references and is excluded from this iteration. Manual smoke-test via the demo sandbox below is the current verification path for form generation.

### `.mjs` extension

The Node scripts under `tests/` and `plugins/acss-kit/scripts/lib/` use `.mjs` to make their ES module format explicit at the file level. `tests/package.json` also sets `"type": "module"`; the explicit `.mjs` extension keeps the scripts unambiguous when read or executed in isolation, independent of which `package.json` is in scope.

### Escape hatch when the harness itself blocks unrelated work

The harness has no `--skip` flag by design. If a regression in one of the validators is genuinely blocking work that has nothing to do with the failing check, the documented escape hatch is:

1. In your branch only, comment out the offending step in `tests/run.sh`.
2. Open a follow-up issue describing the validator bug and link it from your PR description.
3. The reviewer can sign off as long as the bug fix is tracked.

This is the literal-only escape — there is no `SKIP_TESTS=1` env var. Use it sparingly.

## Storybook deep check: `tests/storybook.sh`

Optional, opt-in. ~3–4 minutes including a Playwright browser download on first run. Run before merging anything render-sensitive.

```sh
npx playwright install      # one-time
tests/storybook.sh
```

What it adds beyond `tests/run.sh`:
- Live render verification (a component throws on mount).
- Runtime DOM accessibility audits via `axe-playwright` against every story.

What it does NOT add: theme contrast (no Storybook story for CSS-only files), SCSS contract violations that render but break the rules, manifest checks. Run `tests/run.sh` *first* — `tests/storybook.sh` is supplementary, not a replacement.

## Quick local test: `--plugin-dir`

The fastest way to test a plugin without the marketplace install flow is the `--plugin-dir` flag. Claude Code loads the plugin directly from the local path, so changes to SKILL.md and command files are picked up on the next `claude` invocation without re-running the install.

```sh
# Run tests/setup.sh first if the sandbox doesn't exist yet
tests/setup.sh

# cd into the sandbox, then launch Claude with the plugin loaded directly
cd tests/sandbox
claude --plugin-dir ../../plugins/acss-kit
```

Once Claude starts, verify the plugin loaded:

```text
/plugin list
```

Then run smoke commands as normal (`/kit-list`, `/kit-add button`, etc.). No `/plugin marketplace add` or `/plugin install` step needed.

Use this path for rapid iteration on SKILL.md prose or command front-matter. Switch to the full marketplace flow (below) when you want to validate the install path itself.

## Demo sandbox: `tests/setup.sh`

Recreates the original Vite + React + TypeScript sandbox flow for end-to-end slash-command verification.

### Prerequisites

- Node 20+ and npm on `PATH`
- Claude Code CLI (`claude`) on `PATH`

### One-shot setup

From the repo root:

```sh
tests/setup.sh
```

The script:

1. Verifies `node`, `npm`, `git`, and `.claude-plugin/marketplace.json`.
2. Scaffolds a fresh Vite + React + TypeScript project at `tests/sandbox/`.
3. Installs `sass`, which `acss-kit` needs for generated SCSS.
4. Initializes a git repo inside the sandbox and makes one bootstrap commit.
5. Writes `tests/sandbox/RECIPE.md` and prints the same recipe to stdout.

Re-run with `--reset` to wipe and recreate the sandbox.

### Running the recipe

```sh
cd tests/sandbox
claude
```

Inside the Claude Code session, paste the block from `RECIPE.md`:

```text
/plugin marketplace add <absolute path printed by the script>
/plugin install acss-kit@acss-plugins
```

The local marketplace suffix is `acss-plugins`, from the `name` field in `.claude-plugin/marketplace.json`.

### Smoke flow

```text
/plugin list
/kit-list
/kit-add button card
/theme-create "#4f46e5" --mode=both
```

What to verify:

- `/plugin list` shows `acss-kit`.
- `/kit-list` is read-only and lists the component catalog.
- `/kit-add button card` creates `.acss-target.json`, `<componentsDir>/ui.tsx`, and generated Button/Card TSX + SCSS files.
- `/theme-create "#4f46e5" --mode=both` creates `src/styles/theme/light.css` and `src/styles/theme/dark.css`.
- `npm run build` in the sandbox succeeds.
- `git status` inside the sandbox shows only expected generated files.

Optional form pilot check:

```text
Create a signup form with email and password.
```

The `component-form` skill should auto-trigger, vendor any missing form dependencies through `/kit-add`, and write a form under `src/forms/`.

### Reset

```sh
tests/setup.sh --reset
```

Use this between unrelated test sessions or after a plugin run leaves the sandbox in a state you cannot easily reverse.

## Troubleshooting

**`tsc binary missing` or `typescript not installed`**

Run `npm --prefix tests ci` from the repo root.

**`tinycss2 not installed`**

Run `pip3 install --user tinycss2`.

**`Run this script from inside the acss-plugins repo` (setup.sh)**

The script cannot find `.claude-plugin/marketplace.json`. `cd` to the repo root and re-run.

**`Sandbox already exists at: <path>. Re-run with --reset to wipe and recreate it.`**

Expected on a second run. Pass `--reset` if you want a clean rebuild.

**`/plugin install acss-kit@acss-plugins` says "not found"**

Confirm the marketplace was added from the printed absolute repo path. Then run `/plugin marketplace list` and use the listed suffix if your Claude Code version normalizes it differently.

**Plugin command refuses with "dirty tree"**

The bootstrap commit should prevent this on first run. If you already generated files, commit the sandbox changes before re-running commands that guard against dirty trees:

```sh
cd tests/sandbox && git add -A && git commit -m "wip"
```

**`sass` fails to install**

`tests/sandbox/` runs its own `npm install`. If your machine has a registry-blocking firewall or stale npm cache, clear it:

```sh
cd tests/sandbox && npm cache clean --force && npm install
```
