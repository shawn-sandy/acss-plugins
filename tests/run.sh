#!/usr/bin/env bash
# Phase 1 test harness for agentic-acss-plugins.
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
#   7. detect_package_manager.py --self-test.
#   7a. detect_stack.py --self-test (framework + cssPipeline + entrypoint).
#   7b. verify_integration.py --self-test (entrypoint wiring checks).
#   7c. detect_css_entry.py --self-test (CSS/SCSS entry candidates +
#       @import / @use scan).
#   8. acss-utilities validator over plugins/acss-utilities/assets/
#      (selector grammar, var() fallbacks, bridge dark-mode parity,
#      bundle-size budget).
#   9. acss-utilities idempotency: regenerate from utilities.tokens.json
#      and diff against the committed bundle + per-family partials.
#  10. migrate_classnames.py fixture round-trip + idempotency.
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

# Step 7
section "7. detect_package_manager.py --self-test"
DPM_LOG="$TMP_ROOT/detect-pm.log"
if python3 "$REPO_ROOT/plugins/acss-kit/scripts/detect_package_manager.py" --self-test >"$DPM_LOG"; then
  green "detect_package_manager self-test OK"
else
  red "detect_package_manager self-test FAILED:"
  cat "$DPM_LOG"
  exit 1
fi

section "7a. detect_stack.py --self-test"
DS_LOG="$TMP_ROOT/detect-stack.log"
if python3 "$REPO_ROOT/plugins/acss-kit/scripts/detect_stack.py" --self-test >"$DS_LOG"; then
  green "detect_stack self-test OK"
else
  red "detect_stack self-test FAILED:"
  cat "$DS_LOG"
  exit 1
fi

section "7b. verify_integration.py --self-test"
VI_LOG="$TMP_ROOT/verify-integration.log"
if python3 "$REPO_ROOT/plugins/acss-kit/scripts/verify_integration.py" --self-test >"$VI_LOG"; then
  green "verify_integration self-test OK"
else
  red "verify_integration self-test FAILED:"
  cat "$VI_LOG"
  exit 1
fi

section "7c. detect_css_entry.py --self-test"
DCE_LOG="$TMP_ROOT/detect-css-entry.log"
if python3 "$REPO_ROOT/plugins/acss-kit/scripts/detect_css_entry.py" --self-test >"$DCE_LOG"; then
  green "detect_css_entry self-test OK"
else
  red "detect_css_entry self-test FAILED:"
  cat "$DCE_LOG"
  exit 1
fi

section "7d. kit-sync manifest scripts (hash_file + manifest_write + manifest_read + diff_status)"
KS_LOG="$TMP_ROOT/kit-sync.log"
if python3 "$REPO_ROOT/plugins/acss-kit/scripts/diff_status.py" --self-test >"$KS_LOG"; then
  green "kit-sync manifest self-test OK"
else
  red "kit-sync manifest self-test FAILED:"
  cat "$KS_LOG"
  exit 1
fi

# Step 8
section "8. acss-utilities validator"
UTIL_DIR="$REPO_ROOT/plugins/acss-utilities/assets"
if [ -d "$UTIL_DIR" ]; then
  UTIL_LOG="$TMP_ROOT/utilities-validate.log"
  if python3 "$REPO_ROOT/plugins/acss-utilities/scripts/validate_utilities.py" "$UTIL_DIR" >"$UTIL_LOG"; then
    green "acss-utilities validator OK"
  else
    red "acss-utilities validator failed:"
    cat "$UTIL_LOG"
    exit 1
  fi
else
  yellow "no plugins/acss-utilities/assets — skipping utilities validator"
fi

# Step 9
section "9. acss-utilities idempotency"
if [ -f "$UTIL_DIR/utilities.tokens.json" ]; then
  UTIL_REGEN_DIR="$TMP_ROOT/utilities-regen"
  mkdir -p "$UTIL_REGEN_DIR"
  REGEN_LOG="$TMP_ROOT/utilities-regen.log"
  if ! python3 "$REPO_ROOT/plugins/acss-utilities/scripts/generate_utilities.py" \
         --tokens "$UTIL_DIR/utilities.tokens.json" \
         --out-dir "$UTIL_REGEN_DIR" >"$REGEN_LOG" 2>&1; then
    red "acss-utilities generator failed:"
    cat "$REGEN_LOG"
    exit 1
  fi
  IDEMPOTENT=1
  if ! diff -q "$UTIL_DIR/utilities.css" "$UTIL_REGEN_DIR/utilities.css" >/dev/null; then
    IDEMPOTENT=0
  fi
  if ! diff -qr "$UTIL_DIR/utilities/" "$UTIL_REGEN_DIR/utilities/" >/dev/null; then
    IDEMPOTENT=0
  fi
  if [ "$IDEMPOTENT" -eq 0 ]; then
    red "acss-utilities idempotency check failed — regenerated bundle diverges from the committed copy."
    red "Run \`python3 plugins/acss-utilities/scripts/generate_utilities.py --tokens \\"
    red "  plugins/acss-utilities/assets/utilities.tokens.json --out-dir plugins/acss-utilities/assets/\` and commit."
    diff "$UTIL_DIR/utilities.css" "$UTIL_REGEN_DIR/utilities.css" | head -40 || true
    exit 1
  fi
  green "acss-utilities idempotency OK"
else
  yellow "no plugins/acss-utilities/assets/utilities.tokens.json — skipping idempotency check"
fi

# Step 10
section "10. migrate_classnames.py fixture round-trip + idempotency"
MIGRATE_SCRIPT="$REPO_ROOT/plugins/acss-utilities/scripts/migrate_classnames.py"
FIXTURES_DIR="$REPO_ROOT/plugins/acss-utilities/scripts/tests/migrate_fixtures"
if [ -f "$MIGRATE_SCRIPT" ] && [ -d "$FIXTURES_DIR" ]; then
  MIGRATE_LOG="$TMP_ROOT/migrate-classnames.log"
  MIGRATE_FAIL=0
  MIGRATE_TMP="$TMP_ROOT/migrate-fixtures"
  mkdir -p "$MIGRATE_TMP"
  for before in "$FIXTURES_DIR"/*.before.*; do
    [ -f "$before" ] || continue
    bname="$(basename "$before")"
    ext="${bname##*.}"
    stem="${bname%.before.*}"
    after="$FIXTURES_DIR/${stem}.after.${ext}"
    [ -f "$after" ] || continue
    tmp_copy="$MIGRATE_TMP/${bname}"
    cp "$before" "$tmp_copy"
    # Run once (write mode)
    python3 "$MIGRATE_SCRIPT" "$tmp_copy" --write >/dev/null 2>&1
    # Compare to .after fixture
    if ! diff -q "$tmp_copy" "$after" >/dev/null 2>&1; then
      echo "FAIL (round-trip): $stem" >> "$MIGRATE_LOG"
      diff "$after" "$tmp_copy" >> "$MIGRATE_LOG" 2>&1 || true
      MIGRATE_FAIL=1
      continue
    fi
    # Run again (idempotency)
    cp "$tmp_copy" "${tmp_copy}.orig"
    python3 "$MIGRATE_SCRIPT" "$tmp_copy" --write >/dev/null 2>&1
    if ! diff -q "${tmp_copy}.orig" "$tmp_copy" >/dev/null 2>&1; then
      echo "FAIL (idempotency): $stem" >> "$MIGRATE_LOG"
      MIGRATE_FAIL=1
    fi
    rm -f "${tmp_copy}.orig"
  done
  if [ "$MIGRATE_FAIL" -eq 0 ]; then
    green "migrate_classnames fixture tests OK"
  else
    red "migrate_classnames fixture tests FAILED:"
    cat "$MIGRATE_LOG"
    exit 1
  fi
else
  yellow "migrate_classnames.py or fixtures not found — skipping"
fi

section "ALL STEPS GREEN"
green "Phase 1 harness passed."
