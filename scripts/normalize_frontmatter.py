#!/usr/bin/env python3
"""Normalize frontmatter YAML keys to lowercase across all wiki pages."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
WIKI_PAGES = ROOT / "wiki" / "pages"
PAGE_CATEGORIES = ["sources", "entities", "concepts", "syntheses", "claims", "data", "interventions"]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)^---\s*\n", re.MULTILINE | re.DOTALL)

def normalize_frontmatter(text: str) -> tuple[str, bool]:
    """Lowercase YAML keys in frontmatter block. Returns (new_text, changed)."""
    if not text.startswith("---\n"):
        return text, False
    match = FRONTMATTER_RE.match(text)
    if not match:
        return text, False
    fm = match.group(1)
    changed = False
    lines = fm.splitlines(keepends=True)
    new_lines = []
    for line in lines:
        # Match YAML key at start of line: key:
        m = re.match(r"^([A-Za-z0-9_-]+)(:\s*)", line)
        if m:
            key = m.group(1)
            lower_key = key.lower()
            if key != lower_key:
                line = lower_key + m.group(2) + line[m.end():]
                changed = True
        new_lines.append(line)
    if not changed:
        return text, False
    new_fm = "".join(new_lines)
    new_text = "---\n" + new_fm + "---\n" + text[match.end():]
    return new_text, True


def main() -> None:
    total = 0
    changed = 0
    files_changed = []
    for category in PAGE_CATEGORIES:
        for path in sorted((WIKI_PAGES / category).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            new_text, was_changed = normalize_frontmatter(text)
            total += 1
            if was_changed:
                path.write_text(new_text, encoding="utf-8")
                changed += 1
                files_changed.append(str(path.relative_to(ROOT)))
    print(f"Checked {total} pages")
    print(f"Normalized {changed} pages")
    if files_changed:
        print("Files changed:")
        for f in files_changed:
            print(f"  {f}")


if __name__ == "__main__":
    main()
