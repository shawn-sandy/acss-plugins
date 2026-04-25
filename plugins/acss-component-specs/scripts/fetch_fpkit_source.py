#!/usr/bin/env python3
"""
fetch_fpkit_source.py — Fetch fpkit component source from GitHub and cache locally.

Cache location: assets/fpkit-cache/<sha>/<component>.tsx
SHA is the resolved HEAD of the fpkit main branch at fetch time.
Cache is valid for 7 days; --refresh forces a re-fetch.

Used by /spec-add to populate fpkit_version in spec frontmatter.

Usage:
    python fetch_fpkit_source.py button
    python fetch_fpkit_source.py button --refresh
    python fetch_fpkit_source.py nav --refresh

Output: JSON to stdout.
  {
    "ok": true,
    "data": {
      "component": "button",
      "sha": "abc1234",
      "cache_path": "assets/fpkit-cache/abc1234/button.tsx",
      "source_url": "https://raw.githubusercontent.com/shawn-sandy/acss/main/...",
      "fetched": true
    },
    "reasons": []
  }

Exit 0 on success, 1 on failure.
"""

import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path


FPKIT_BASE = "https://raw.githubusercontent.com/shawn-sandy/acss/main/packages/fpkit/src/components"
FPKIT_COMMIT_API = "https://api.github.com/repos/shawn-sandy/acss/commits/main"
CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days

# Component name → source path within fpkit repo
COMPONENT_PATHS = {
    'button': 'buttons/btn.tsx',
    'card': 'cards/card.tsx',
    'dialog': 'dialogs/dialog.tsx',
    'alert': 'alerts/alert.tsx',
    'nav': 'navs/nav.tsx',
    'stack': 'stack/stack.tsx',
    'form': 'forms/form.tsx',
    'badge': 'badges/badge.tsx',
    'tag': 'tags/tag.tsx',
    'icon': 'icons/icon.tsx',
}

CACHE_BASE = Path(__file__).parent.parent / 'assets/fpkit-cache'


def _fail(reasons):
    print(json.dumps({"ok": False, "data": None, "reasons": reasons}))
    sys.exit(1)


def _fetch_url(url, timeout=15):
    """Fetch URL content. Returns (bytes, error_str)."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'acss-component-specs/0.1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read(), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.reason} — {url}"
    except urllib.error.URLError as e:
        return None, f"URL error: {e.reason} — {url}"
    except Exception as e:
        return None, f"Fetch error: {e} — {url}"


def _get_latest_sha():
    """Resolve HEAD SHA of acss main branch via GitHub API."""
    data, err = _fetch_url(FPKIT_COMMIT_API)
    if err:
        return None, f"Could not resolve HEAD SHA: {err}"
    try:
        obj = json.loads(data.decode('utf-8'))
        return obj['sha'][:8], None  # Short SHA (8 chars)
    except Exception as e:
        return None, f"Could not parse GitHub API response: {e}"


def _find_cached(component, sha):
    """Return cached file path if it exists and is non-empty."""
    candidate = CACHE_BASE / sha / f'{component}.tsx'
    if candidate.exists() and candidate.stat().st_size > 0:
        return candidate
    return None


def _find_any_cached(component):
    """Find any cached version (newest by mtime) for a component."""
    candidates = list(CACHE_BASE.glob(f'*/{component}.tsx'))
    if not candidates:
        return None, None
    newest = max(candidates, key=lambda p: p.stat().st_mtime)
    sha = newest.parent.name
    # Check if cache is still fresh
    age = time.time() - newest.stat().st_mtime
    if age < CACHE_TTL_SECONDS:
        return newest, sha
    return None, None


def main():
    args = sys.argv[1:]
    if not args:
        _fail(["Usage: fetch_fpkit_source.py <component> [--refresh]"])

    component = args[0].lower()
    do_refresh = '--refresh' in args

    if not do_refresh:
        cached_path, cached_sha = _find_any_cached(component)
        if cached_path:
            print(json.dumps({
                "ok": True,
                "data": {
                    "component": component,
                    "sha": cached_sha,
                    "cache_path": str(cached_path),
                    "source_url": f"{FPKIT_BASE}/{COMPONENT_PATHS.get(component, component + '.tsx')}",
                    "fetched": False,
                },
                "reasons": ["Using cached source (< 7 days old). Use --refresh to force re-fetch."],
            }))
            sys.exit(0)

    # Resolve latest SHA
    sha, err = _get_latest_sha()
    if err:
        # Fall back to 'main' as the version label
        sha = 'main'
        reasons = [f"Could not resolve exact SHA ({err}); using 'main' as version label."]
    else:
        reasons = []

    # Determine source path
    rel_path = COMPONENT_PATHS.get(component)
    if not rel_path:
        # Try common patterns as fallback
        rel_path = f'{component}s/{component}.tsx'
        reasons.append(f"Component '{component}' not in known path map; trying {rel_path}")

    source_url = f"{FPKIT_BASE}/{rel_path}"
    content, err = _fetch_url(source_url)

    if err:
        # Try alternate path pattern
        alt_path = f'{component}/{component}.tsx'
        alt_url = f"{FPKIT_BASE}/{alt_path}"
        content, alt_err = _fetch_url(alt_url)
        if alt_err:
            _fail([
                f"Could not fetch source for '{component}':",
                f"  Primary: {err}",
                f"  Fallback: {alt_err}",
                "Add the component path to COMPONENT_PATHS in fetch_fpkit_source.py.",
            ])
        source_url = alt_url

    # Write to cache
    cache_dir = CACHE_BASE / sha
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f'{component}.tsx'
    cache_path.write_bytes(content)

    print(json.dumps({
        "ok": True,
        "data": {
            "component": component,
            "sha": sha,
            "cache_path": str(cache_path),
            "source_url": source_url,
            "fetched": True,
            "bytes": len(content),
        },
        "reasons": reasons,
    }, indent=2))
    sys.exit(0)


if __name__ == '__main__':
    main()
