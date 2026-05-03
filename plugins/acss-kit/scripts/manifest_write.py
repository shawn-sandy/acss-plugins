#!/usr/bin/env python3
"""
Atomically write or merge .acss-kit/manifest.json at a project root.

Reads a JSON payload from stdin describing the manifest entries to upsert,
merges them with any existing manifest (preserving entries not mentioned in
the payload), and writes the result atomically (write-temp + rename).

Stdin payload shape:

    {
      "projectRoot": "/abs/path",
      "pluginVersion": "0.9.0",
      "targetDir": "src/components/fpkit",
      "stylesDir": "src/styles",
      "themeFile": "acss-kit.theme.json",
      "files": [
        {
          "path": "src/components/fpkit/button.tsx",
          "sha256": "<hex>",
          "kind": "component",
          "source": "ref:components/button.md#tsx-template",
          "component": "button"
        }
      ],
      "removePaths": ["src/components/fpkit/old.tsx"]
    }

Optional fields default to existing manifest values (or empty). `removePaths`
lets callers prune entries that no longer exist on disk.

Output (JSON to stdout):

    {
      "ok": true,
      "path": "/abs/.acss-kit/manifest.json",
      "filesWritten": 5,
      "filesRemoved": 0,
      "reasons": []
    }

Exit codes:
    0 — manifest written
    1 — logical failure (malformed payload)
    2 — IO error
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
import tempfile
from pathlib import Path


MANIFEST_REL = ".acss-kit/manifest.json"
SCHEMA_VERSION = 1


def _now() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class _ExistingUnreadable(Exception):
    pass


def _read_existing(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        raise _ExistingUnreadable(f"existing manifest unreadable: {e}") from e
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        # Refuse to overwrite a corrupt manifest — caller can repair or delete.
        raise _ExistingUnreadable(f"existing manifest is not valid JSON: {e}") from e
    if not isinstance(data, dict):
        raise _ExistingUnreadable("existing manifest is not a JSON object")
    return data


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".manifest-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"manifest_write: invalid JSON on stdin: {e}", file=sys.stderr)
        return 1

    if not isinstance(payload, dict):
        print(
            f"manifest_write: payload must be a JSON object, got {type(payload).__name__}",
            file=sys.stderr,
        )
        return 1

    project_root = payload.get("projectRoot")
    if not project_root:
        print("manifest_write: payload missing 'projectRoot'", file=sys.stderr)
        return 1

    root = Path(project_root).resolve()
    manifest_path = root / MANIFEST_REL
    try:
        existing = _read_existing(manifest_path)
    except _ExistingUnreadable as e:
        print(f"manifest_write: {e}", file=sys.stderr)
        return 1

    files = existing.get("files", {})
    if not isinstance(files, dict):
        files = {}

    payload_files = payload.get("files", []) or []
    if not isinstance(payload_files, list):
        print(
            f"manifest_write: 'files' must be a JSON array, got {type(payload_files).__name__}",
            file=sys.stderr,
        )
        return 1

    written = 0
    skipped: list[str] = []
    for entry in payload_files:
        if not isinstance(entry, dict):
            skipped.append(repr(entry))
            continue
        rel = entry.get("path")
        sha = entry.get("sha256")
        kind = entry.get("kind")
        if not (rel and sha and kind):
            skipped.append(repr(entry))
            continue
        files[rel] = {
            "source": entry.get("source", ""),
            "sha256": sha,
            "pluginVersion": payload.get("pluginVersion", existing.get("pluginVersion", "")),
            "kind": kind,
        }
        if entry.get("component"):
            files[rel]["component"] = entry["component"]
        written += 1

    removed = 0
    remove_paths = payload.get("removePaths", []) or []
    if not isinstance(remove_paths, list):
        print(
            f"manifest_write: 'removePaths' must be a JSON array, got {type(remove_paths).__name__}",
            file=sys.stderr,
        )
        return 1
    for rel in remove_paths:
        if isinstance(rel, str) and rel in files:
            del files[rel]
            removed += 1

    out = {
        "schemaVersion": SCHEMA_VERSION,
        "pluginVersion": payload.get("pluginVersion", existing.get("pluginVersion", "")),
        "targetDir": payload.get("targetDir", existing.get("targetDir", "")),
        "stylesDir": payload.get("stylesDir", existing.get("stylesDir", "")),
        "themeFile": payload.get("themeFile", existing.get("themeFile", "")),
        "generatedAt": _now(),
        "files": files,
    }

    try:
        _atomic_write(manifest_path, json.dumps(out, indent=2) + "\n")
    except OSError as e:
        print(f"manifest_write: {e}", file=sys.stderr)
        return 2

    reasons: list[str] = []
    if skipped:
        reasons.append(
            f"Skipped {len(skipped)} payload entry/entries missing required fields (path, sha256, kind)."
        )

    print(json.dumps({
        "ok": True,
        "path": str(manifest_path),
        "filesWritten": written,
        "filesRemoved": removed,
        "filesSkipped": len(skipped),
        "reasons": reasons,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
