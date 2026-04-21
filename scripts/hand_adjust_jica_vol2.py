#!/usr/bin/env python3
"""Hand-curated adjustments to the jica-ipsdp-main-report-vol2 decisions YAML.

Run this AFTER curate_jica_vol2_decisions.py. It applies a small number of
explicit (page, image_index) overrides chosen by visually reviewing each row
for subject/target alignment — things a heuristic can't do reliably.

Each adjustment carries a short 'why' so a future reader can see the reasoning.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pdf_atlas_lib import (  # noqa: E402
    dump_decision_rows,
    get_source,
    parse_decisions_text,
    source_abs_path,
)


SOURCE_ID = "jica-ipsdp-main-report-vol2"


ADJUSTMENTS = {
    (270, 0): ("drop", "", "", "caption is Seti Nadi profile, target marsyangdi; no seti-nadi page exists"),
    (286, 0): ("drop", "", "", "caption is Rapti profile, target madi; subject mismatch"),
    (274, 0): ("drop", "", "", "caption is Sun Koshi profile, target upper-bhotekoshi; no sun-koshi page"),
    (176, 0): ("drop", "", "", "Figure 4.1-1 National Power Policy 2013 is a generic policy figure, not lower-badigad specific"),
    (177, 0): ("drop", "", "", "Table 4.1-3 is an aggregate status table (text > pixels), not lower-badigad specific"),
    (36, 0): ("drop", "", "", "caption describes Middle Mountain / Siwalik geographic zones, not NEA"),
    (112, 0): ("drop", "", "", "caption is a truncated body sentence ('Figure 2.6-3 shows trends ...'), not a figure title"),
    (254, 0): ("drop", "", "", "caption is a legend key (STO/ROR/PROR), not meaningful on upper-karnali"),
    (32, 0): ("drop", "", "", "caption is only a lat/long fragment; image value too low without real title"),
    (109, 1): ("drop", "", "", "duplicate of p109 i0 (same 'Figure 2.5-4 Power Interruption' caption)"),
    (264, 0): ("reroute", "kali-gandaki-kowan", "Figure 6.3-10 River Longitudinal Profile of the Kali Gandaki River (Upstream)", "caption is Kali Gandaki upstream profile; kali-gandaki-kowan is the upstream storage project"),
    (277, 0): ("reroute", "likhu-4", "Figure 6.3-21 River Longitudinal Profile of the Likhu Khola River", "caption is Likhu Khola; likhu-4 HEP is on that river"),
}


def main() -> None:
    source = get_source(SOURCE_ID)
    yaml_path = source_abs_path(source, "decisions_v2_yaml")
    rows = parse_decisions_text(yaml_path.read_text(encoding="utf-8"))

    applied = 0
    for row in rows:
        key = (int(row["page"]), int(row["image_index"]))
        if key not in ADJUSTMENTS:
            continue
        verb, slug, caption, why = ADJUSTMENTS[key]
        if verb == "drop":
            row["action"] = "drop"
            row["target_slug"] = ""
            row["proposed_slug"] = ""
            row["paragraph_anchor"] = ""
            row["note"] = f"hand-adjust:drop; {why}"
        elif verb == "reroute":
            row["target_slug"] = slug
            row["proposed_slug"] = ""
            row["paragraph_anchor"] = ""
            if caption:
                row["caption"] = caption
            row["note"] = f"hand-adjust:reroute-to-{slug}; {why}"
        applied += 1

    yaml_path.write_text(dump_decision_rows(rows), encoding="utf-8")
    print(f"wrote={yaml_path}")
    print(f"adjustments_applied={applied}")


if __name__ == "__main__":
    main()
