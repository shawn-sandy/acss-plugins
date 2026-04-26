#!/usr/bin/env bash
# Phase 2 deep-check harness: Storybook + axe-playwright.
#
# Runs the optional Storybook deep check. Slower than tests/run.sh
# (~3-4 min including Playwright browser download on first run).
# Catches live render errors and runtime DOM accessibility violations
# that the static harness cannot.
#
# Run tests/run.sh FIRST. This script does not duplicate its checks.
#
# Prerequisites:
#   - Node 20+ and npm.
#   - Playwright browser bundle (`npx playwright install` once).

set -eo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HARNESS="$REPO_ROOT/plugins/acss-kit/.harness"

red()    { printf '\033[31m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }
section(){ printf '\n\033[1m== %s ==\033[0m\n' "$*"; }

if [ ! -d "$HARNESS" ]; then
  red "Harness scaffold missing at $HARNESS"
  exit 1
fi

# Step 1
section "1. install storybook deps (if needed)"
if [ ! -d "$HARNESS/node_modules" ]; then
  # `npm install` (not `ci`): the harness gitignores its package-lock.json
  # because the deep-check is opt-in dev tooling, not a reproducible
  # build artifact.
  yellow "node_modules/ missing — running npm install (one-time, ~2-3 min)"
  npm --prefix "$HARNESS" install
else
  green "deps already installed"
fi

# Step 2
section "2. generate stories from Usage Examples"
node "$REPO_ROOT/plugins/acss-kit/scripts/generate_stories.mjs"

# Step 3
section "3. build storybook"
npm --prefix "$HARNESS" run build-storybook

# Step 4
section "4. run test-storybook"
yellow "If this is the first run on this machine, run \`npx playwright install\` first."
npm --prefix "$HARNESS" run test-storybook

green "Storybook deep check passed."
