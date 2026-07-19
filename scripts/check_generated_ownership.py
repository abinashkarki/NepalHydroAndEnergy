#!/usr/bin/env python3
"""Validate the generated asset ownership manifest."""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "docs" / "generated-assets.json"
REQUIRED_FIELDS = {"owner", "command", "inputs", "committed", "deployable"}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{MANIFEST.relative_to(ROOT)} is not valid JSON: {exc}")

    if data.get("version") != 1:
        fail("docs/generated-assets.json version must be 1")
    assets = data.get("assets")
    if not isinstance(assets, dict) or not assets:
        fail("docs/generated-assets.json must contain a non-empty assets object")

    missing_outputs: list[str] = []
    for output, entry in assets.items():
        if not isinstance(entry, dict):
            fail(f"manifest entry for {output} must be an object")
        missing = REQUIRED_FIELDS - set(entry)
        if missing:
            fail(f"manifest entry for {output} missing fields: {', '.join(sorted(missing))}")
        if not isinstance(entry["inputs"], list) or not entry["inputs"]:
            fail(f"manifest entry for {output} must list at least one input")
        if not isinstance(entry["committed"], bool) or not isinstance(entry["deployable"], bool):
            fail(f"manifest entry for {output} committed/deployable must be booleans")
        if not str(entry["owner"]).strip() or not str(entry["command"]).strip():
            fail(f"manifest entry for {output} must have non-empty owner and command")

        if "*" in output:
            matches = list(ROOT.glob(output))
            if not matches:
                missing_outputs.append(output)
        elif not (ROOT / output).exists():
            missing_outputs.append(output)

    if missing_outputs:
        fail("generated ownership manifest points to missing output(s):\n" + "\n".join(missing_outputs))

    print(f"OK: {len(assets)} generated asset ownership entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
