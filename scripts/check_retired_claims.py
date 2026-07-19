#!/usr/bin/env python3
"""Fail when retired public claims or drafting residue reappear."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "retired_claims.json"


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    failures: list[str] = []
    for rule in registry.get("rules", []):
        patterns = [str(value).casefold() for value in rule.get("patterns", [])]
        for root_name in registry.get("scan_roots", []):
            scan_root = ROOT / root_name
            if scan_root.is_file():
                paths = [scan_root]
            else:
                paths = sorted(
                    path
                    for path in scan_root.rglob("*")
                    if path.suffix in {".md", ".json", ".html", ".js"}
                )
            for path in paths:
                for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    folded = line.casefold()
                    for pattern in patterns:
                        if pattern in folded:
                            failures.append(
                                f"{path.relative_to(ROOT)}:{line_no}: {rule['id']}: {line.strip()}"
                            )
    if failures:
        print("FAIL: retired public claims or production residue found")
        for failure in failures:
            print(f"  {failure}")
        raise SystemExit(1)
    print(f"OK: {len(registry.get('rules', []))} retired-claim rules clear")


if __name__ == "__main__":
    main()
