#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class SourceUsedByTests(unittest.TestCase):
    def test_source_used_by_sections_match_exact_backlinks(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/check_source_used_by.py"],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
