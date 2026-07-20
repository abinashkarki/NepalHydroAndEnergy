#!/usr/bin/env python3
"""Validate the recorded production wiki release.

The record is historical: asset hashes are checked against the recorded Git
commit, not against the current worktree, so development after a release does
not invalidate the production record.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "release" / "production.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
REQUIRED_STRING_FIELDS = {
    "environment",
    "public_url",
    "release_version",
    "wiki_repository",
    "wiki_ref",
    "wiki_commit",
    "transparentgov_repository",
    "transparentgov_commit",
    "deployed_at",
    "verified_at",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def git(*args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=text,
    )
    if result.returncode:
        stderr = result.stderr.strip() if text else result.stderr.decode().strip()
        fail(f"git {' '.join(args)} failed: {stderr}")
    return result.stdout.strip() if text else result.stdout


def main() -> None:
    try:
        record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {RECORD_PATH.relative_to(ROOT)}: {exc}")

    if record.get("schema_version") != 1:
        fail("schema_version must be 1")

    for field in sorted(REQUIRED_STRING_FIELDS):
        if not isinstance(record.get(field), str) or not record[field].strip():
            fail(f"{field} must be a non-empty string")

    if record["environment"] != "production":
        fail("environment must be production")
    if not VERSION_RE.fullmatch(record["release_version"]):
        fail("release_version must use semantic version syntax without a leading v")

    for field in ("wiki_ref", "wiki_commit", "transparentgov_commit"):
        if not SHA_RE.fullmatch(record[field]):
            fail(f"{field} must be a full lowercase 40-character commit SHA")
    if record["wiki_ref"] != record["wiki_commit"]:
        fail("wiki_ref must equal wiki_commit; production must use an immutable ref")

    parsed_url = urlparse(record["public_url"])
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        fail("public_url must be an absolute HTTPS URL")

    wiki_commit = record["wiki_commit"]
    git("cat-file", "-e", f"{wiki_commit}^{{commit}}")

    verification = record.get("verification")
    if not isinstance(verification, dict):
        fail("verification must be an object")
    if not isinstance(verification.get("page_count"), int) or verification["page_count"] < 1:
        fail("verification.page_count must be a positive integer")
    assets = verification.get("assets")
    if not isinstance(assets, dict) or not assets:
        fail("verification.assets must contain at least one asset hash")

    for asset_path, expected_hash in sorted(assets.items()):
        if not isinstance(asset_path, str) or asset_path.startswith(("/", "../")):
            fail(f"unsafe asset path in release record: {asset_path!r}")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            fail(f"invalid SHA-256 for {asset_path}")
        blob = git("show", f"{wiki_commit}:{asset_path}", text=False)
        actual_hash = hashlib.sha256(blob).hexdigest()
        if actual_hash != expected_hash:
            fail(
                f"recorded hash mismatch for {asset_path}: "
                f"expected {expected_hash}, got {actual_hash}"
            )

    index_blob = git(
        "show",
        f"{wiki_commit}:wiki/explorer/shared/wiki-page-index.json",
        text=False,
    )
    try:
        page_index = json.loads(index_blob)
    except json.JSONDecodeError as exc:
        fail(f"recorded page index is invalid JSON: {exc}")
    if page_index.get("totalPages") != verification["page_count"]:
        fail(
            "verification.page_count does not match totalPages at the recorded "
            f"commit ({page_index.get('totalPages')})"
        )

    print(
        "Release record valid: "
        f"v{record['release_version']} at {wiki_commit} "
        f"({verification['page_count']} pages, {len(assets)} checked assets)"
    )


if __name__ == "__main__":
    main()
