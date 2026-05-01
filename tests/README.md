# Local Plugin Testing

Three complementary paths: an automated structural validation gate, an automated end-to-end skill-output check, and a manual demo fixture for exercising slash commands.

| Path | Command | When to run | What it catches |
|------|---------|-------------|-----------------|
| Structural validation | `tests/run.sh` | Before every PR; after editing any reference doc | Banned imports, malformed TSX, missing `var()` fallbacks, theme contrast regressions, manifest/structure drift |
| End-to-end skill output | `tests/e2e.sh` | Before merging anything render-sensitive; before release | Generated TSX type-checks against React types, generated SCSS compiles, generated HTML passes structural axe-core a11y rules, expected file tree |
| Demo fixture | `tests/setup.sh` | When changing slash-command prose; for interactive smoke testing | Manual visual confirmation that `/kit-add`, `/theme-create`, etc. produce reasonable output |

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

For a deeper check that the extracted TSX *also* type-checks against real React types, see `tests/e2e.sh` below.

### Component Form gap

`skills/component-form/SKILL.md` is **not yet covered** by this harness. The form skill uses richer placeholder substitution (`{{FIELDS}}`) than the simple component references and is excluded from this iteration. Manual smoke-test via the demo fixture below is the current verification path for form generation.

### `.mjs` extension

The Node scripts under `tests/` and `plugins/acss-kit/scripts/lib/` use `.mjs` to make their ES module format explicit at the file level. `tests/package.json` also sets `"type": "module"`; the explicit `.mjs` extension keeps the scripts unambiguous when read or executed in isolation, independent of which `package.json` is in scope.

### Escape hatch when the harness itself blocks unrelated work

The harness has no `--skip` flag by design. If a regression in one of the validators is genuinely blocking work that has nothing to do with the failing check, the documented escape hatch is:

1. In your branch only, comment out the offending step in `tests/run.sh`.
2. Open a follow-up issue describing the validator bug and link it from your PR description.
3. The reviewer can sign off as long as the bug fix is tracked.

This is the literal-only escape — there is no `SKIP_TESTS=1` env var. Use it sparingly.

## End-to-end skill output: `tests/e2e.sh`

The deeper opt-in check. Replaces the previous Storybook + Playwright + axe-playwright path. Runs in a per-invocation temp dir so it never clobbers `tests/sandbox/`.

```sh
# Same one-time setup as tests/run.sh
npm --prefix tests ci

# Every run
tests/e2e.sh
```

What it does, in order:
1. **Self-test the a11y harness.** Runs `run_axe.mjs --self-test` against `tests/fixtures/known-bad-a11y/violation.html`. If axe-core ever stops flagging the deliberate violations, the run fails fast — preventing a misleading green on real output.
2. **Resolve dependencies and extract components.** A small dependency walker (`tests/lib/resolve_deps.mjs`) mirrors Step B3 in `skills/components/SKILL.md` so compound components like Dialog/IconButton pull their leaf dependencies. Each resolved component is extracted from its reference doc via the shared `extract.mjs` and written into the fixture at `src/components/fpkit/<name>/`.
3. **Generate a theme.** Runs the same Python pipeline `/theme-create` runs (`generate_palette.py | tokens_to_css.py`) against a known seed color, producing `light.css` and `dark.css`.
4. **Validate theme contrast.** Runs `validate_theme.py` against the generated files (same WCAG 2.2 AA pairs as `tests/run.sh`).
5. **Type-check.** `tsc --noEmit` against the fixture's `tsconfig.json`, with React + types resolved via the symlinked `tests/node_modules`. The fixture includes an ambient `declare module '*.scss';` so component imports of stylesheet modules type-check.
6. **Compile SCSS.** Runs `sass --no-source-map` over every generated `.scss` file and asserts each one parses.
7. **Render and audit.** `tests/lib/render_components.mjs` bundles each component with esbuild (stubbing SCSS/CSS imports), renders it to static HTML via `react-dom/server`, and writes one `.html` file per component. `run_axe.mjs --html` then runs axe-core inside jsdom and fails on any `serious` or `critical` violations.
8. **Assert expected file tree.** Confirms `ui.tsx`, the seed components' TSX/SCSS, and both theme CSS files all landed at the standard paths.

### What jsdom + axe-core catches vs. doesn't

The previous Storybook + Playwright path ran in a real browser. jsdom does not lay out, does not compute styles, and does not run real interactivity, so this check is strictly less powerful. Concretely:

| Catches | Does not catch |
|---|---|
| Missing `alt` on images | Real color contrast on rendered pixels |
| Missing accessible names on buttons / form controls | Visible-focus indicators (`:focus-visible` styling) |
| Illegal nesting / role conflicts | Hidden-by-CSS detection (`display: none`) |
| Missing `lang` on `<html>` | Keyboard order and focus traps |
| ARIA reference / state inconsistencies | Animation- or scroll-driven a11y issues |

Theme color contrast is still covered separately by `validate_theme.py` in `tests/run.sh` — only contrast regressions caused by component-level CSS overrides would slip through, and those are rare. Author review remains the backstop for the right-column items.

### Adding a new component to e2e coverage

`tests/e2e.sh` exercises a small seed set (button, link, input). To extend coverage, add a fixture entry to `DEFAULT_PROPS` in `tests/lib/render_components.mjs` — the entry is the minimal-but-realistic invocation needed to render meaningful HTML for that component. Components without a fixture are skipped with a warning, not a failure, so adding a new component to the catalog doesn't immediately break this harness.

### Honest scope

`tests/e2e.sh` verifies **artifact correctness** — do the generated files compile, type-check, render without a11y violations. It does not verify **skill orchestration** — does the LLM-driven prose in `SKILL.md` make the right decisions about what to extract or when to refuse. That second check still rides on author review and the manual demo fixture below.

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

## Demo fixture: `tests/setup.sh`

A minimal verification fixture for end-to-end slash-command verification. No Vite, no Storybook, no app shell — just a `package.json`, a `tsconfig.json`, and an ambient SCSS module declaration. There is no `npm run dev` in this fixture; previewing rendered components in a real browser was explicitly removed because the goal is to test the skill output, not to render a React app.

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
2. Writes `package.json`, `tsconfig.json`, `src/scss-modules.d.ts`, and `src/.gitkeep` directly — no `npm create`.
3. Runs one `npm install` for the pinned devDeps (typescript, sass, react, react-dom, types).
4. Initializes a git repo inside the sandbox and makes one bootstrap commit.
5. Writes `tests/sandbox/RECIPE.md` and prints the same recipe to stdout.

Re-run with `--reset` to wipe and recreate the fixture.

### Running the recipe

```sh
cd tests/sandbox
claude
```

Inside the Claude Code session, paste the block from `RECIPE.md`:

```text
/plugin marketplace add <absolute path printed by the script>
/plugin install acss-kit@agentic-acss-plugins
```

The local marketplace suffix is `agentic-acss-plugins`, from the `name` field in `.claude-plugin/marketplace.json`.

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
- `npm run typecheck` in the sandbox succeeds (runs `tsc --noEmit`).
- Optionally compile a generated SCSS file: `npx sass --no-source-map src/components/fpkit/button/button.scss`.
- `git status` inside the sandbox shows only expected generated files.

Optional form pilot check:

```text
Create a signup form with email and password.
```

The `component-form` skill should auto-trigger, vendor any missing form dependencies through `/kit-add`, and write a form under `src/forms/`.

- **Optional:** to visually verify a generated component's CSS variants in a browser, see [Preview a generated component in a browser](../plugins/acss-kit/docs/recipes.md#preview-a-generated-component-in-a-browser). This is a static-HTML preview, not a revival of the removed dev server.

### Reset

```sh
tests/setup.sh --reset
```

Use this between unrelated test sessions or after a plugin run leaves the fixture in a state you cannot easily reverse.

## Troubleshooting

**`tsc binary missing` or `typescript not installed`**

Run `npm --prefix tests ci` from the repo root.

**`tinycss2 not installed`**

Run `pip3 install --user tinycss2`.

**`tests/node_modules missing` (e2e.sh)**

Run `npm --prefix tests ci` from the repo root.

**`Run this script from inside the agentic-acss-plugins repo` (setup.sh)**

The script cannot find `.claude-plugin/marketplace.json`. `cd` to the repo root and re-run.

**`Sandbox already exists at: <path>. Re-run with --reset to wipe and recreate it.`**

Expected on a second run. Pass `--reset` if you want a clean rebuild.

**`/plugin install acss-kit@agentic-acss-plugins` says "not found"**

Confirm the marketplace was added from the printed absolute repo path. Then run `/plugin marketplace list` and use the listed suffix if your Claude Code version normalizes it differently.

**Plugin command refuses with "dirty tree"**

The bootstrap commit should prevent this on first run. If you already generated files, commit the sandbox changes before re-running commands that guard against dirty trees:

```sh
cd tests/sandbox && git add -A && git commit -m "wip"
```

**`SELF-TEST FAILED: known-bad-a11y fixture produced no violations` (e2e.sh)**

`tests/run_axe.mjs --self-test` could not find the deliberate violations in `tests/fixtures/known-bad-a11y/violation.html`. Either axe-core regressed across a version bump, the fixture lost its violation in an edit, or the harness wiring is broken. Investigate before trusting any green result on real component output.
