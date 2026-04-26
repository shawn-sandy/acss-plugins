# Local Plugin Testing

Smoke-test the `acss-kit` marketplace entry by installing it into a disposable Vite + React + TypeScript sandbox.

The sandbox lives at `tests/sandbox/` and is gitignored. Only the scaffolding (`setup.sh`, this file) is committed, so contributors can recreate the same starting point with one command.

## Prerequisites

- Node 20+ and npm on `PATH`
- Claude Code CLI (`claude`) on `PATH`

## One-Shot Setup

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

## Running The Recipe

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

## Smoke Flow

These commands prove the surviving consolidated plugin paths work:

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

## Reset

```sh
tests/setup.sh --reset
```

Use this between unrelated test sessions or after a plugin run leaves the sandbox in a state you cannot easily reverse.

## What This Does Not Cover

- Automated assertions on Claude Code slash command output.
- Full accessibility audits of generated React output.
- Browser rendering checks.

## Troubleshooting

**`Run this script from inside the acss-plugins repo`**

The script cannot find `.claude-plugin/marketplace.json`. `cd` to the repo root and re-run.

**`Sandbox already exists at: <path>. Re-run with --reset to wipe and recreate it.`**

Expected on a second run. Pass `--reset` if you want a clean rebuild.

**`/plugin install acss-kit@acss-plugins` says "not found"`**

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
