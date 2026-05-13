#!/usr/bin/env python3
"""Build the wiki brief blocks and persona briefing packs.

A "brief" is a structured top-of-page summary card: one headline, one short
"what this is" paragraph, four to six metrics, one traffic-light signal, and
one "why it matters" line. The brief block is the unit of content that
powers persona briefing packs and the explorer's signal badges.

Inputs
------
* Every wiki page that declares a `brief:` block in YAML frontmatter.
* For operating-project entity pages without a `brief:` block, a best-effort
  fallback is auto-derived from `data/project_specs.csv` (used only to power
  the JSON index; never injected as a visible markdown block).

Outputs
-------
* `wiki/explorer/shared/wiki-briefs.json` (machine-readable index keyed by slug)
* `wiki/explorer/briefing-packs/{policymakers,investors,journalists}.md`
  (downloadable markdown packs aggregated by the `audiences:` field)
* With `--inject`: visible `<!-- generated:brief:start -->` ...
  `<!-- generated:brief:end -->` markdown blocks inserted/refreshed near the
  top of each page that carries a `brief:` frontmatter block.

Usage
-----
    python scripts/build_briefs.py                     # dry-run report
    python scripts/build_briefs.py --write             # write JSON index only
    python scripts/build_briefs.py --write --inject    # also inject markdown
    python scripts/build_briefs.py --write --inject --packs
                                                       # also write briefing packs
"""
from __future__ import annotations

import argparse
import csv as csv_module
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WIKI_PAGES = ROOT / "wiki" / "pages"
SHARED = ROOT / "wiki" / "explorer" / "shared"
BRIEFS_JSON = SHARED / "wiki-briefs.json"
PACK_DIR = ROOT / "wiki" / "explorer" / "briefing-packs"
SPECS_CSV = ROOT / "data" / "project_specs.csv"

CATEGORIES = ["sources", "entities", "concepts", "syntheses", "claims", "data", "interventions"]

BRIEF_START = "<!-- generated:brief:start -->"
BRIEF_END = "<!-- generated:brief:end -->"

VALID_SIGNALS = {"green", "amber", "red"}
VALID_AUDIENCES = {"policymakers", "investors", "journalists"}

PACK_HEADERS = {
    "policymakers": {
        "title": "Nepal Energy Wiki — Briefing Pack for Policymakers",
        "blurb": (
            "Sourced, traceable, structured briefs on the most-cited claims, "
            "projects, and interventions in Nepal's electricity system. "
            "Every metric in this pack links back to a wiki page with the "
            "underlying source. Built from `wiki/pages/` by "
            "`scripts/build_briefs.py`."
        ),
    },
    "investors": {
        "title": "Nepal Energy Wiki — Briefing Pack for Investors",
        "blurb": (
            "Per-project and system-level briefs covering capacity, generation, "
            "tariff, financial structure, and current signal. This pack is a "
            "public knowledge product, **not investment advice**. Use it for "
            "context; verify project-level financials in audited filings."
        ),
    },
    "journalists": {
        "title": "Nepal Energy Wiki — Briefing Pack for Journalists",
        "blurb": (
            "Story-ready evidence with sources. Every brief lists six numbers "
            "and a traffic-light signal so a reporter can verify the headline "
            "before deadline. Citations live one click away on the linked "
            "wiki page."
        ),
    },
}


# --------------------------------------------------------------------------- #
#  Frontmatter handling                                                       #
# --------------------------------------------------------------------------- #
def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 4)
    if end == -1:
        return "", text
    return text[4:end].strip(), text[end + 4 :].lstrip("\n")


def parse_brief(fm_yaml: str) -> dict | None:
    if not fm_yaml:
        return None
    try:
        data = yaml.safe_load(fm_yaml) or {}
    except yaml.YAMLError:
        return None
    return data.get("brief") if isinstance(data, dict) else None


# --------------------------------------------------------------------------- #
#  Validation                                                                  #
# --------------------------------------------------------------------------- #
def validate_brief(slug: str, brief: dict) -> list[str]:
    errs: list[str] = []
    if not isinstance(brief, dict):
        return [f"{slug}: brief is not a mapping"]
    headline = brief.get("headline")
    if not isinstance(headline, str) or not headline.strip():
        errs.append(f"{slug}: brief.headline missing or empty")
    elif len(headline) > 200:
        errs.append(f"{slug}: brief.headline > 200 chars ({len(headline)})")
    what = brief.get("what")
    if what is not None and not isinstance(what, str):
        errs.append(f"{slug}: brief.what must be a string")
    elif isinstance(what, str) and len(what) > 600:
        errs.append(f"{slug}: brief.what > 600 chars ({len(what)})")
    metrics = brief.get("metrics") or []
    if not isinstance(metrics, list):
        errs.append(f"{slug}: brief.metrics must be a list")
    else:
        if len(metrics) < 4:
            errs.append(f"{slug}: brief.metrics has {len(metrics)} entries (minimum 4)")
        if len(metrics) > 6:
            errs.append(f"{slug}: brief.metrics has {len(metrics)} entries (maximum 6)")
        for idx, m in enumerate(metrics):
            if not isinstance(m, dict):
                errs.append(f"{slug}: brief.metrics[{idx}] must be a mapping")
                continue
            label = m.get("label")
            value = m.get("value")
            if not isinstance(label, str) or not label.strip():
                errs.append(f"{slug}: brief.metrics[{idx}].label missing")
            if value is None or (isinstance(value, str) and not value.strip()):
                errs.append(f"{slug}: brief.metrics[{idx}].value missing")
    signal = brief.get("signal")
    if signal is not None and signal not in VALID_SIGNALS:
        errs.append(f"{slug}: brief.signal must be one of {sorted(VALID_SIGNALS)}; got {signal!r}")
    signal_note = brief.get("signal_note")
    if signal_note is not None and not isinstance(signal_note, str):
        errs.append(f"{slug}: brief.signal_note must be a string")
    why = brief.get("why_it_matters")
    if why is not None and not isinstance(why, str):
        errs.append(f"{slug}: brief.why_it_matters must be a string")
    audiences = brief.get("audiences") or []
    if not isinstance(audiences, list):
        errs.append(f"{slug}: brief.audiences must be a list")
    else:
        bad = [a for a in audiences if a not in VALID_AUDIENCES]
        if bad:
            errs.append(f"{slug}: brief.audiences has unknown entries {bad}; valid: {sorted(VALID_AUDIENCES)}")
    return errs


# --------------------------------------------------------------------------- #
#  Visible markdown block rendering                                            #
# --------------------------------------------------------------------------- #
def render_brief_markdown(brief: dict) -> str:
    headline = (brief.get("headline") or "").strip()
    what = (brief.get("what") or "").strip()
    metrics = brief.get("metrics") or []
    signal = brief.get("signal")
    signal_note = (brief.get("signal_note") or "").strip()
    why = (brief.get("why_it_matters") or "").strip()

    lines: list[str] = [BRIEF_START, "", "## Brief", ""]

    if signal in VALID_SIGNALS:
        label = signal.capitalize()
        note_segment = f" {signal_note}" if signal_note else ""
        lines.append(
            f'<p class="wiki-brief-signal" data-signal="{signal}">'
            f"<strong>Signal: {label}.</strong>{note_segment}</p>"
        )
        lines.append("")

    lead_parts: list[str] = []
    if headline:
        lead_parts.append(f"**{headline}**")
    if what:
        lead_parts.append(what)
    if lead_parts:
        lines.append(" ".join(lead_parts))
        lines.append("")

    if metrics:
        labels = [str(m.get("label", "")).strip() for m in metrics]
        values = [str(m.get("value", "")).strip() for m in metrics]
        lines.append("| " + " | ".join(labels) + " |")
        lines.append("|" + "---|" * len(labels))
        lines.append("| " + " | ".join(values) + " |")
        lines.append("")

    if why:
        lines.append(f"_Why it matters: {why}_")
        lines.append("")

    lines.append(BRIEF_END)
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
#  Injection                                                                   #
# --------------------------------------------------------------------------- #
TITLE_LINE_RE = re.compile(r"^(#\s+.+?)$", re.MULTILINE)


def inject_brief_block(md_text: str, new_block: str) -> tuple[str, bool]:
    """Insert or replace the generated brief block.

    Placement rule: the block goes immediately after the first H1 heading
    (the page title), or after the frontmatter if no H1 is present.
    """
    if BRIEF_START in md_text and BRIEF_END in md_text:
        pattern = re.compile(re.escape(BRIEF_START) + r".*?" + re.escape(BRIEF_END), re.DOTALL)
        new_text = pattern.sub(new_block, md_text, count=1)
        return new_text, new_text != md_text

    # Locate the first H1 in the body (after the closing ---).
    if md_text.startswith("---"):
        end = md_text.find("\n---", 4)
        if end != -1:
            head = md_text[: end + 4]
            tail = md_text[end + 4 :]
        else:
            head, tail = "", md_text
    else:
        head, tail = "", md_text

    m = TITLE_LINE_RE.search(tail)
    if m:
        cut = m.end()
        new_tail = tail[:cut] + "\n\n" + new_block + "\n" + tail[cut:]
    else:
        new_tail = "\n\n" + new_block + "\n" + tail.lstrip("\n")
    new_text = head + new_tail
    return new_text, True


# --------------------------------------------------------------------------- #
#  Auto-derive from project_specs.csv                                          #
# --------------------------------------------------------------------------- #
def load_specs() -> dict[str, dict[str, str]]:
    if not SPECS_CSV.exists():
        return {}
    out: dict[str, dict[str, str]] = {}
    with SPECS_CSV.open(newline="", encoding="utf-8-sig") as f:
        reader = csv_module.DictReader(f)
        for row in reader:
            slug = (row.get("slug") or "").strip()
            if not slug:
                continue
            out[slug] = {k.strip(): str(v).strip() for k, v in row.items() if k and str(v).strip()}
    return out


def derive_brief_from_specs(slug: str, spec: dict[str, str], title: str) -> dict | None:
    """Best-effort brief derivation for operating projects with no hand-authored
    brief. Returned only for JSON index, never injected into pages."""
    if not spec:
        return None
    status = (spec.get("status") or "").lower()
    if status not in {"operating", "under-construction"}:
        return None

    def pick(key: str, suffix: str = "") -> str | None:
        v = spec.get(key)
        if not v:
            return None
        return f"{v}{suffix}"

    metrics: list[dict] = []
    cap = pick("capacity_mw", " MW")
    if cap:
        metrics.append({"label": "Capacity", "value": cap})
    ann = pick("annual_design_energy_gwh", " GWh/yr")
    if ann:
        metrics.append({"label": "Design energy", "value": ann})
    plf = pick("plant_load_factor_pct", "%")
    if plf:
        metrics.append({"label": "PLF", "value": plf})
    dry = pick("dry_share_pct", "%")
    if dry:
        metrics.append({"label": "Dry share", "value": dry})
    ppa_w = spec.get("ppa_rate_wet_npr_kwh")
    ppa_d = spec.get("ppa_rate_dry_npr_kwh")
    if ppa_w or ppa_d:
        metrics.append({"label": "PPA wet/dry (NPR/kWh)", "value": f"{ppa_w or '—'} / {ppa_d or '—'}"})
    cod = pick("cod_year")
    if cod:
        metrics.append({"label": "COD", "value": cod})

    if len(metrics) < 4:
        return None

    return {
        "_auto_derived": True,
        "headline": f"{title} — {cap or 'capacity unknown'}, {status.replace('-', ' ')}.",
        "what": f"Auto-derived registry summary. See the page for engineering, governance, and source context.",
        "metrics": metrics[:6],
        "signal": None,
        "signal_note": None,
        "why_it_matters": None,
        "audiences": [],
    }


# --------------------------------------------------------------------------- #
#  Collection                                                                  #
# --------------------------------------------------------------------------- #
TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)
TYPE_RE = re.compile(r"^type:\s*(.+?)\s*$", re.MULTILINE)


def collect_pages() -> list[dict]:
    """Walk wiki/pages/ and return per-page info needed for brief building."""
    pages: list[dict] = []
    for cat in CATEGORIES:
        d = WIKI_PAGES / cat
        if not d.exists():
            continue
        for md in sorted(d.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            fm, _body = split_frontmatter(text)
            title_m = TITLE_RE.search(fm)
            type_m = TYPE_RE.search(fm)
            pages.append({
                "slug": md.stem,
                "path": md,
                "category": cat,
                "title": title_m.group(1).strip() if title_m else md.stem,
                "type": type_m.group(1).strip() if type_m else cat[:-1] if cat.endswith("s") else cat,
                "frontmatter": fm,
                "text": text,
                "brief": parse_brief(fm),
            })
    return pages


# --------------------------------------------------------------------------- #
#  Main                                                                        #
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="Write wiki-briefs.json")
    ap.add_argument("--inject", action="store_true", help="Inject visible brief markdown into pages")
    ap.add_argument("--packs", action="store_true", help="Write persona briefing-pack markdown files")
    args = ap.parse_args()

    pages = collect_pages()
    specs = load_specs()

    authored: list[dict] = []
    derived: list[dict] = []
    errors: list[str] = []
    injected = 0

    for p in pages:
        if p["brief"]:
            errs = validate_brief(p["slug"], p["brief"])
            if errs:
                errors.extend(errs)
                continue
            entry = {
                "slug": p["slug"],
                "title": p["title"],
                "category": p["category"],
                "type": p["type"],
                "source": "authored",
                **p["brief"],
            }
            authored.append(entry)
            if args.inject:
                block = render_brief_markdown(p["brief"])
                new_text, changed = inject_brief_block(p["text"], block)
                if changed:
                    # Bump frontmatter `updated:` to today for traceability.
                    new_text = re.sub(
                        r"^updated:\s*.+$",
                        f"updated: {dt.date.today().isoformat()}",
                        new_text,
                        count=1,
                        flags=re.MULTILINE,
                    )
                    p["path"].write_text(new_text, encoding="utf-8")
                    injected += 1
        else:
            # Try auto-derived (operating projects only, JSON only — never injected).
            if p["category"] == "entities":
                auto = derive_brief_from_specs(p["slug"], specs.get(p["slug"], {}), p["title"])
                if auto:
                    entry = {
                        "slug": p["slug"],
                        "title": p["title"],
                        "category": p["category"],
                        "type": p["type"],
                        "source": "auto-derived",
                        **auto,
                    }
                    derived.append(entry)

    # ----------------------------------------------------------------------- #
    # Report                                                                  #
    # ----------------------------------------------------------------------- #
    print(f"pages scanned:        {len(pages)}")
    print(f"authored briefs:      {len(authored)}")
    print(f"auto-derived briefs:  {len(derived)} (operating/under-construction projects without hand-authored brief)")
    if errors:
        print()
        print(f"VALIDATION ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        return 1
    if args.inject:
        print(f"injected/refreshed brief blocks: {injected}")

    # ----------------------------------------------------------------------- #
    # JSON index                                                              #
    # ----------------------------------------------------------------------- #
    if args.write:
        SHARED.mkdir(parents=True, exist_ok=True)
        index = {
            "version": 1,
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "authored": authored,
            "auto_derived": derived,
        }
        BRIEFS_JSON.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {BRIEFS_JSON.relative_to(ROOT)} ({len(authored)} authored, {len(derived)} derived)")

    # ----------------------------------------------------------------------- #
    # Briefing packs                                                          #
    # ----------------------------------------------------------------------- #
    if args.packs:
        PACK_DIR.mkdir(parents=True, exist_ok=True)
        today = dt.date.today().isoformat()
        for persona, meta in PACK_HEADERS.items():
            entries = [b for b in authored if persona in (b.get("audiences") or [])]
            md_lines: list[str] = []
            md_lines.append(f"# {meta['title']}")
            md_lines.append("")
            md_lines.append(meta["blurb"])
            md_lines.append("")
            md_lines.append(f"_Generated {today} from {len(entries)} authored briefs._")
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
            md_lines.append("## Contents")
            md_lines.append("")
            if not entries:
                md_lines.append("_No briefs are tagged for this audience yet. Add `audiences: [" + persona + "]` to a page's `brief:` block to include it here._")
                md_lines.append("")
            else:
                for entry in entries:
                    md_lines.append(f"- [{entry['title']}](#{entry['slug']}) — {entry['headline']}")
                md_lines.append("")
                md_lines.append("---")
                md_lines.append("")
                for entry in entries:
                    md_lines.append(f'<a id="{entry["slug"]}"></a>')
                    md_lines.append("")
                    md_lines.append(f"## {entry['title']}")
                    md_lines.append("")
                    md_lines.append(f"_{entry['category']} · `{entry['slug']}`_")
                    md_lines.append("")
                    if entry.get("signal") in VALID_SIGNALS:
                        label = entry["signal"].capitalize()
                        note = entry.get("signal_note") or ""
                        md_lines.append(f"**Signal: {label}.** {note}")
                        md_lines.append("")
                    md_lines.append(f"**{entry['headline']}**")
                    md_lines.append("")
                    if entry.get("what"):
                        md_lines.append(entry["what"])
                        md_lines.append("")
                    metrics = entry.get("metrics") or []
                    if metrics:
                        md_lines.append("| " + " | ".join(m["label"] for m in metrics) + " |")
                        md_lines.append("|" + "---|" * len(metrics))
                        md_lines.append("| " + " | ".join(str(m["value"]) for m in metrics) + " |")
                        md_lines.append("")
                    if entry.get("why_it_matters"):
                        md_lines.append(f"_Why it matters: {entry['why_it_matters']}_")
                        md_lines.append("")
                    md_lines.append(f"Source page: `wiki/pages/{entry['category']}/{entry['slug']}.md`")
                    md_lines.append("")
                    md_lines.append("---")
                    md_lines.append("")
            (PACK_DIR / f"{persona}.md").write_text("\n".join(md_lines), encoding="utf-8")
            print(f"wrote briefing pack: {PACK_DIR.relative_to(ROOT)}/{persona}.md ({len(entries)} briefs)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
