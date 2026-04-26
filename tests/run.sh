#!/usr/bin/env bash
# Phase 1 test harness for acss-plugins.
#
# Runs the full structural validation gate. SERIAL ONLY — concurrent
# runs in the same checkout will collide on tests/.tmp/. If you need
# parallelism, run in separate worktrees.
#
# Steps:
#   1. Wipe tests/.tmp/.
#   2. Extract TSX/SCSS from acss-kit reference docs and syntax-check
#      the extracted TSX with TypeScript's parser API.
#   3. SCSS contract validation.
#   4. WCAG theme contrast (existing tool, lives under the plugin).
#   5. Manifest / structure replication of verify-plugins.
#   6. Known-bad self-tests: confirm the validators catch their own
#      contract violations.
#
# Why syntax-only TSX validation: the reference docs split TSX across
# multiple Key Pattern sections containing illustrative JSX or
# inline-only snippets that don't resolve at module scope. Full type
# resolution would require either inlining helpers (fighting the docs'
# documentary structure) or accepting non-trivial false negatives.
# Syntax checks catch what regex can't (malformed JSX, broken generics)
# without that fight.
#
# If a step in this script regresses and blocks unrelated work, the
# documented escape hatch is to comment out the offending step in your
# branch and link a bug report in the PR description (see tests/README.md).

set -eo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

TMP_ROOT="$REPO_ROOT/tests/.tmp"
EXTRACTED="$TMP_ROOT/extracted"

red()    { printf '\033[31m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }
section(){ printf '\n\033[1m== %s ==\033[0m\n' "$*"; }

# Step 1
section "1. wipe tests/.tmp/"
rm -rf "$TMP_ROOT"
mkdir -p "$EXTRACTED"

# Step 2
section "2. extract + syntax-check acss-kit references"
node "$REPO_ROOT/tests/validate_components.mjs"

# Step 3
section "3. SCSS contract"
SCSS_LOG="$TMP_ROOT/scss-contract.log"
if python3 "$REPO_ROOT/tests/validate_components.py" "$EXTRACTED" >"$SCSS_LOG"; then
  green "SCSS contract OK"
else
  red "SCSS contract failed:"
  cat "$SCSS_LOG"
  exit 1
fi

# Step 4
section "4. WCAG theme contrast"
THEME_DIR="$REPO_ROOT/plugins/acss-kit/assets"
THEME_LOG="$TMP_ROOT/theme-contrast.log"
if compgen -G "$THEME_DIR/themes/*.css" > /dev/null; then
  if python3 "$REPO_ROOT/plugins/acss-kit/scripts/validate_theme.py" "$THEME_DIR/themes/"*.css >"$THEME_LOG"; then
    green "theme contrast OK"
  else
    red "theme contrast failed:"
    cat "$THEME_LOG"
    exit 1
  fi
elif [ -f "$THEME_DIR/brand-template.css" ]; then
  yellow "no themes/*.css yet; brand-template.css is the only theme on disk — skipping WCAG check"
else
  yellow "no theme css under $THEME_DIR — skipping WCAG check"
fi

# Step 5
section "5. manifest / structure"
MANIFEST_LOG="$TMP_ROOT/manifest.log"
if python3 "$REPO_ROOT/tests/validate_manifest.py" >"$MANIFEST_LOG"; then
  green "manifest OK"
else
  red "manifest validation failed:"
  cat "$MANIFEST_LOG"
  exit 1
fi

# Step 6
section "6. known-bad self-tests"
KNOWN_BAD_TMP="$TMP_ROOT/known-bad"
mkdir -p "$KNOWN_BAD_TMP"
cp "$REPO_ROOT/tests/fixtures/known-bad/known-bad.scss" "$KNOWN_BAD_TMP/"

# (a) SCSS validator must FAIL on known-bad.scss
if python3 "$REPO_ROOT/tests/validate_components.py" "$KNOWN_BAD_TMP" >/dev/null 2>&1; then
  red "known-bad: validate_components.py PASSED on known-bad fixtures (regex regressed)"
  exit 1
fi
green "SCSS validator caught known-bad.scss"

# (b) TSX validator must reject the banned import in known-bad.tsx.
# Build a synthetic reference doc using known-bad.tsx as its TSX Template,
# then call the *exported* checkImports() from validate_components.mjs
# directly. This exercises the real validator code path; a stub regex
# here would let import-allowlist regressions slip through.
KNOWN_BAD_REF="$KNOWN_BAD_TMP/known-bad.md"
{
  printf '%s\n\n' '# Component: KnownBad'
  printf '%s\n\n' '## Props Interface'
  printf '%s\n' '```tsx'
  printf '%s\n' 'export type KnownBadProps = { children?: React.ReactNode }'
  printf '%s\n' '```'
  printf '\n%s\n\n' '## TSX Template'
  printf '%s\n' '```tsx'
  cat "$REPO_ROOT/tests/fixtures/known-bad/known-bad.tsx"
  printf '%s\n' '```'
  printf '\n%s\n\n' '## SCSS Template'
  printf '%s\n' '```scss'
  printf '%s\n' '.known-bad { padding: 1rem; }'
  printf '%s\n' '```'
  printf '\n%s\n' '## Accessibility'
} > "$KNOWN_BAD_REF"

KNOWN_BAD_REF_PATH="$KNOWN_BAD_REF" node --input-type=module -e "
import { extractFromFile } from '$REPO_ROOT/plugins/acss-kit/scripts/lib/extract.mjs';
import { checkImports } from '$REPO_ROOT/tests/validate_components.mjs';

const { tsx } = extractFromFile(process.env.KNOWN_BAD_REF_PATH);
if (!tsx) { console.error('known-bad: no tsx extracted'); process.exit(1); }

const failures = checkImports('known-bad', tsx);
if (failures.length === 0) {
  console.error('known-bad: validate_components.mjs accepted banned import in synthetic reference');
  process.exit(1);
}
console.log('known-bad: TSX validator caught', failures.length, 'failure(s)');
"

green "TSX validator caught known-bad.tsx"

section "ALL STEPS GREEN"
green "Phase 1 harness passed."
