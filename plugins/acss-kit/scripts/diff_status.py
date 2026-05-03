#!/usr/bin/env python3
"""
Drift detector for kit-sync. Compares each file recorded in
.acss-kit/manifest.json against its current on-disk content and classifies
it as clean, modified, or missing.

The "clean" classification means: the file exists and its sha256 (after the
shared kit-sync normalization rules) matches the manifest. /kit-update
overwrites clean files freely. Modified files are skipped unless --force.

Usage:
    python3 diff_status.py [project_root]

Output (JSON to stdout):

    {
      "ok": true,
      "projectRoot": "/abs/path",
      "manifestPath": "/abs/.acss-kit/manifest.json",
      "clean":    [{"path": "...", "kind": "...", "component": "..."}, ...],
      "modified": [{"path": "...", "kind": "...", "currentSha": "...", "expectedSha": "..."}],
      "missing":  [{"path": "...", "kind": "..."}],
      "totals":   {"clean": N, "modified": N, "missing": N},
      "reasons": []
    }

Exit codes:
    0 — diff computed (regardless of drift counts)
    1 — manifest missing or unreadable (no diff possible)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Local import — _hash_bytes is duplicated logic intentionally so this script
# stays runnable standalone. It mirrors hash_file.py's normalize() exactly.
import hashlib
import re


_TRAILING_WS_RE = re.compile(rb"[ \t]+(?=\n)")


def _normalize(raw: bytes) -> bytes:
    text = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    text = _TRAILING_WS_RE.sub(b"", text)
    text = re.sub(rb"\n+\Z", b"\n", text)
    if text and not text.endswith(b"\n"):
        text = text + b"\n"
    return text


def _sha256_normalized(p: Path) -> str:
    return hashlib.sha256(_normalize(p.read_bytes())).hexdigest()


def _self_test() -> int:
    """End-to-end exercise of hash_file + manifest_write + manifest_read + diff_status.

    Sets up a temp project, writes a tracked file, builds a manifest, then
    asserts diff_status classifies the file correctly under three scenarios:
    untouched (clean), edited (modified), deleted (missing).
    """
    import json as _json
    import subprocess
    import tempfile

    here = Path(__file__).resolve().parent

    def _run(cmd: list[str], stdin: str | None = None) -> tuple[int, str, str]:
        p = subprocess.run(cmd, input=stdin, capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    failures: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        target = root / "src" / "components" / "fpkit"
        target.mkdir(parents=True)
        sample = target / "button.tsx"
        sample_content = "export const Button = () => null\n"
        sample.write_text(sample_content, encoding="utf-8")

        # 1. Hash via hash_file.py
        rc, out, err = _run(
            ["python3", str(here / "hash_file.py"), "--path", str(sample)]
        )
        if rc != 0:
            failures.append(f"hash_file.py exited {rc}: {err}")
            print("\n".join(failures), file=sys.stderr)
            return 1
        sha = _json.loads(out)["sha256"]

        # 2. Write manifest via manifest_write.py
        payload = {
            "projectRoot": str(root),
            "pluginVersion": "0.0.0-test",
            "targetDir": "src/components/fpkit",
            "stylesDir": "src/styles",
            "themeFile": "acss-kit.theme.json",
            "files": [
                {
                    "path": "src/components/fpkit/button.tsx",
                    "sha256": sha,
                    "kind": "component",
                    "source": "ref:components/button.md#tsx-template",
                    "component": "button",
                }
            ],
        }
        rc, out, err = _run(
            ["python3", str(here / "manifest_write.py")],
            stdin=_json.dumps(payload),
        )
        if rc != 0:
            failures.append(f"manifest_write.py exited {rc}: {err}")

        # 3. manifest_read.py should now report exists=true
        rc, out, err = _run(["python3", str(here / "manifest_read.py"), str(root)])
        if rc != 0:
            failures.append(f"manifest_read.py exited {rc}: {err}")
        else:
            data = _json.loads(out)
            if not data.get("exists"):
                failures.append("manifest_read: exists is False after write")
            if "src/components/fpkit/button.tsx" not in data.get("files", {}):
                failures.append("manifest_read: tracked path missing from files{}")

        # 4. diff_status — clean
        rc, out, err = _run(["python3", str(here / "diff_status.py"), str(root)])
        diff = _json.loads(out)
        if diff["totals"] != {"clean": 1, "modified": 0, "missing": 0}:
            failures.append(f"diff (untouched) totals wrong: {diff['totals']}")

        # 5. Modify the file → diff should report modified
        sample.write_text(sample_content + "// edit\n", encoding="utf-8")
        rc, out, err = _run(["python3", str(here / "diff_status.py"), str(root)])
        diff = _json.loads(out)
        if diff["totals"] != {"clean": 0, "modified": 1, "missing": 0}:
            failures.append(f"diff (edited) totals wrong: {diff['totals']}")

        # 6. Delete the file → diff should report missing
        sample.unlink()
        rc, out, err = _run(["python3", str(here / "diff_status.py"), str(root)])
        diff = _json.loads(out)
        if diff["totals"] != {"clean": 0, "modified": 0, "missing": 1}:
            failures.append(f"diff (deleted) totals wrong: {diff['totals']}")

        # 7. Normalization: trailing-whitespace + CRLF must hash equal to LF + clean
        a = target / "a.txt"
        a.write_bytes(b"line one  \nline two\n\n\n")
        b = target / "b.txt"
        b.write_bytes(b"line one\r\nline two\n")
        _, out_a, _ = _run(["python3", str(here / "hash_file.py"), "--path", str(a)])
        _, out_b, _ = _run(["python3", str(here / "hash_file.py"), "--path", str(b)])
        if _json.loads(out_a)["sha256"] != _json.loads(out_b)["sha256"]:
            failures.append("normalization: CRLF/trailing-blank-line variants did not normalize equal")

        # 8. Local _normalize must agree with hash_file.py's normalization for the same input.
        # If the two diverge (e.g. somebody edits one and forgets the other), drift detection
        # produces false "modified" classifications. This catches it in CI.
        sample_bytes = b"x  \r\ny\n\n\n"
        local_sha = hashlib.sha256(_normalize(sample_bytes)).hexdigest()
        rc, out_n, _ = _run(
            ["python3", str(here / "hash_file.py"), "--stdin"],
            stdin=sample_bytes.decode("utf-8"),
        )
        if _json.loads(out_n)["sha256"] != local_sha:
            failures.append("normalization: hash_file.py and diff_status.py _normalize() diverged")

        # 9. manifest_write must reject non-object payloads, non-list 'files', and non-dict entries
        for bad_payload, label in [
            ("[1, 2, 3]", "list payload"),
            ('"hello"', "string payload"),
            ('{"projectRoot": "' + str(root) + '", "files": "not-a-list"}', "non-list files"),
        ]:
            rc, _, _ = _run(["python3", str(here / "manifest_write.py")], stdin=bad_payload)
            if rc != 1:
                failures.append(f"manifest_write accepted {label} (rc={rc}, expected 1)")

        # Non-dict entry inside files[] should be skipped, not crash
        good_with_bad_entry = _json.dumps({
            "projectRoot": str(root),
            "files": ["not-a-dict", {"path": "x.txt", "sha256": sha, "kind": "component"}],
        })
        rc, out_w, _ = _run(["python3", str(here / "manifest_write.py")], stdin=good_with_bad_entry)
        if rc != 0:
            failures.append(f"manifest_write rejected payload with one bad entry (rc={rc}, expected 0)")
        elif _json.loads(out_w).get("filesSkipped", 0) < 1:
            failures.append("manifest_write should report filesSkipped >= 1 for non-dict entry")

        # 10. manifest_read must reject a manifest with non-object 'files'
        bad_manifest = root / ".acss-kit" / "manifest.json"
        bad_manifest.write_text(_json.dumps({"schemaVersion": 1, "files": []}), encoding="utf-8")
        rc, out_r, _ = _run(["python3", str(here / "manifest_read.py"), str(root)])
        if rc != 1:
            failures.append(f"manifest_read accepted non-object 'files' (rc={rc}, expected 1)")

        # And diff_status itself must refuse the same shape gracefully
        rc, out_d, _ = _run(["python3", str(here / "diff_status.py"), str(root)])
        if rc != 1:
            failures.append(f"diff_status accepted non-object 'files' (rc={rc}, expected 1)")

        # 11. Path-traversal guard — manifest entries with absolute or .. paths
        # must be classified as escaping the project root, never read off-tree.
        traversal_manifest = {
            "schemaVersion": 1,
            "pluginVersion": "0.0.0-test",
            "files": {
                "../../etc/passwd": {"source": "x", "sha256": "deadbeef", "kind": "component"},
                "/etc/passwd": {"source": "x", "sha256": "deadbeef", "kind": "component"},
            },
        }
        bad_manifest.write_text(_json.dumps(traversal_manifest), encoding="utf-8")
        rc, out_t, _ = _run(["python3", str(here / "diff_status.py"), str(root)])
        if rc != 0:
            failures.append(f"diff_status traversal case rc={rc}, expected 0")
        else:
            t = _json.loads(out_t)
            modified_paths = {m.get("path") for m in t.get("modified", [])}
            if "../../etc/passwd" not in modified_paths or "/etc/passwd" not in modified_paths:
                failures.append(f"diff_status did not flag traversal entries: {modified_paths}")
            for entry in t.get("modified", []):
                if entry.get("path") in {"../../etc/passwd", "/etc/passwd"}:
                    if entry.get("error") != "Path escapes project root.":
                        failures.append(
                            f"diff_status traversal entry missing escape error: {entry}"
                        )

        # 12. manifest_write must reject non-string path/sha/kind types
        bad_types_payload = _json.dumps({
            "projectRoot": str(root),
            "files": [
                {"path": ["x"], "sha256": "abc", "kind": "component"},
                {"path": "x", "sha256": 123, "kind": "component"},
                {"path": "x", "sha256": "abc", "kind": {"k": "v"}},
            ],
        })
        rc, out_bt, _ = _run(["python3", str(here / "manifest_write.py")], stdin=bad_types_payload)
        if rc != 0:
            failures.append(f"manifest_write rejected payload with bad-type entries (rc={rc}, expected 0)")
        elif _json.loads(out_bt).get("filesSkipped", 0) < 3:
            failures.append("manifest_write should skip all 3 bad-type entries")

    if failures:
        print("diff_status self-test FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("diff_status self-test OK")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        return _self_test()
    start = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    manifest_path = start / ".acss-kit" / "manifest.json"

    if not manifest_path.is_file():
        print(json.dumps({
            "ok": False,
            "projectRoot": str(start),
            "manifestPath": str(manifest_path),
            "clean": [],
            "modified": [],
            "missing": [],
            "totals": {"clean": 0, "modified": 0, "missing": 0},
            "reasons": ["Manifest not found. Run /kit-sync first."],
        }, indent=2))
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({
            "ok": False,
            "projectRoot": str(start),
            "manifestPath": str(manifest_path),
            "clean": [],
            "modified": [],
            "missing": [],
            "totals": {"clean": 0, "modified": 0, "missing": 0},
            "reasons": [f"Manifest unreadable: {e}"],
        }, indent=2))
        return 1

    if not isinstance(manifest, dict):
        print(json.dumps({
            "ok": False,
            "projectRoot": str(start),
            "manifestPath": str(manifest_path),
            "clean": [],
            "modified": [],
            "missing": [],
            "totals": {"clean": 0, "modified": 0, "missing": 0},
            "reasons": [f"Manifest malformed: top-level must be an object, got {type(manifest).__name__}."],
        }, indent=2))
        return 1
    files = manifest.get("files", {})
    if not isinstance(files, dict):
        print(json.dumps({
            "ok": False,
            "projectRoot": str(start),
            "manifestPath": str(manifest_path),
            "clean": [],
            "modified": [],
            "missing": [],
            "totals": {"clean": 0, "modified": 0, "missing": 0},
            "reasons": [f"Manifest malformed: 'files' must be an object, got {type(files).__name__}."],
        }, indent=2))
        return 1

    clean: list[dict] = []
    modified: list[dict] = []
    missing: list[dict] = []

    for rel, entry in files.items():
        if not isinstance(entry, dict):
            continue
        kind = entry.get("kind", "")
        component = entry.get("component")
        expected = entry.get("sha256", "")

        # Defensive: reject manifest entries that escape projectRoot via absolute
        # path or .. traversal. A drift check should never read files the user
        # didn't ask /kit-sync to write.
        if not isinstance(rel, str) or not rel:
            continue
        try:
            abs_path = (start / rel).resolve()
            abs_path.relative_to(start)
        except (ValueError, OSError):
            modified.append({
                "path": rel,
                "kind": kind,
                "currentSha": "",
                "expectedSha": expected,
                "error": "Path escapes project root.",
                **({"component": component} if component else {}),
            })
            continue

        if not abs_path.is_file():
            missing.append({"path": rel, "kind": kind, **({"component": component} if component else {})})
            continue

        try:
            current = _sha256_normalized(abs_path)
        except OSError as e:
            modified.append({
                "path": rel,
                "kind": kind,
                "currentSha": "",
                "expectedSha": expected,
                "error": str(e),
            })
            continue

        if current == expected:
            clean.append({"path": rel, "kind": kind, **({"component": component} if component else {})})
        else:
            modified.append({
                "path": rel,
                "kind": kind,
                "currentSha": current,
                "expectedSha": expected,
                **({"component": component} if component else {}),
            })

    out = {
        "ok": True,
        "projectRoot": str(start),
        "manifestPath": str(manifest_path),
        "clean": clean,
        "modified": modified,
        "missing": missing,
        "totals": {
            "clean": len(clean),
            "modified": len(modified),
            "missing": len(missing),
        },
        "reasons": [],
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
