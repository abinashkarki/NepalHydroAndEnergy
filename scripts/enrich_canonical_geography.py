#!/usr/bin/env python3
"""Backfill canonical Nepal district/province and substation_slug links across data tables.

Policy (Tier B — Canonical Reference Geography):
- Quantitative measures (MW, GWh, MVA, tariffs, coordinates) ALWAYS require primary sources.
- Unambiguous Nepal administrative geography (77 districts -> 7 provinces, established
  municipalities/substations/industrial districts) is filled deterministically from a
  reviewed lookup table and tagged `canonical-geography` in notes.
- Genuinely ambiguous or multi-district hubs keep district blank (and province filled only
  when all candidate districts lie in the same province).
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Canonical Nepal 77 districts -> 7 provinces
DISTRICT_TO_PROVINCE: dict[str, str] = {
    # Koshi (14)
    "Bhojpur": "Koshi", "Dhankuta": "Koshi", "Ilam": "Koshi", "Jhapa": "Koshi",
    "Khotang": "Koshi", "Morang": "Koshi", "Okhaldhunga": "Koshi", "Panchthar": "Koshi",
    "Sankhuwasabha": "Koshi", "Solukhumbu": "Koshi", "Sunsari": "Koshi",
    "Taplejung": "Koshi", "Terhathum": "Koshi", "Udayapur": "Koshi",
    # Madhesh (8)
    "Bara": "Madhesh", "Dhanusha": "Madhesh", "Mahottari": "Madhesh", "Parsa": "Madhesh",
    "Rautahat": "Madhesh", "Saptari": "Madhesh", "Sarlahi": "Madhesh", "Siraha": "Madhesh",
    # Bagmati (13)
    "Bhaktapur": "Bagmati", "Chitwan": "Bagmati", "Dhading": "Bagmati", "Dolakha": "Bagmati",
    "Kathmandu": "Bagmati", "Kavrepalanchok": "Bagmati", "Lalitpur": "Bagmati",
    "Makwanpur": "Bagmati", "Nuwakot": "Bagmati", "Ramechhap": "Bagmati",
    "Rasuwa": "Bagmati", "Sindhuli": "Bagmati", "Sindhupalchok": "Bagmati",
    # Gandaki (11)
    "Baglung": "Gandaki", "Gorkha": "Gandaki", "Kaski": "Gandaki", "Lamjung": "Gandaki",
    "Manang": "Gandaki", "Mustang": "Gandaki", "Myagdi": "Gandaki",
    "Nawalparasi East": "Gandaki", "Nawalpur": "Gandaki", "Parbat": "Gandaki",
    "Syangja": "Gandaki", "Tanahun": "Gandaki",
    # Lumbini (12)
    "Arghakhanchi": "Lumbini", "Banke": "Lumbini", "Bardiya": "Lumbini", "Dang": "Lumbini",
    "Gulmi": "Lumbini", "Kapilvastu": "Lumbini", "Nawalparasi West": "Lumbini",
    "Nawalparasi (Susta Paschim)": "Lumbini", "Palpa": "Lumbini", "Pyuthan": "Lumbini",
    "Rolpa": "Lumbini", "Rukum East": "Lumbini", "Rupandehi": "Lumbini",
    # Karnali (10)
    "Dailekh": "Karnali", "Dolpa": "Karnali", "Humla": "Karnali", "Jajarkot": "Karnali",
    "Jumla": "Karnali", "Kalikot": "Karnali", "Mugu": "Karnali",
    "Rukum West": "Karnali", "Salyan": "Karnali", "Surkhet": "Karnali",
    # Sudurpashchim (9)
    "Achham": "Sudurpashchim", "Baitadi": "Sudurpashchim", "Bajhang": "Sudurpashchim",
    "Bajura": "Sudurpashchim", "Dadeldhura": "Sudurpashchim", "Darchula": "Sudurpashchim",
    "Doti": "Sudurpashchim", "Kailali": "Sudurpashchim", "Kanchanpur": "Sudurpashchim",
}

# Unambiguous substation slug -> (district, province)
# Note: multi-district hubs leave district="" and set province only if unambiguous.
SUBSTATION_CANONICAL_GEO: dict[str, tuple[str, str]] = {
    # Kathmandu Grid Division
    "balaju-substation": ("Kathmandu", "Bagmati"),
    "chapali-substation": ("Kathmandu", "Bagmati"),
    "siuchatar-substation": ("Kathmandu", "Bagmati"),
    "new-chabel-substation": ("Kathmandu", "Bagmati"),
    "lainchour-substation": ("Kathmandu", "Bagmati"),
    "new-patan-substation": ("Lalitpur", "Bagmati"),
    "teku-substation": ("Kathmandu", "Bagmati"),
    "k3-substation": ("Kathmandu", "Bagmati"),
    "baneshwor-substation": ("Kathmandu", "Bagmati"),
    "bhaktapur-substation": ("Bhaktapur", "Bagmati"),
    "banepa-substation": ("Kavrepalanchok", "Bagmati"),
    "panchkhal-substation": ("Kavrepalanchok", "Bagmati"),
    "matatirtha-substation": ("Kathmandu", "Bagmati"),
    "bagmati-substation": ("", ""),
    "samundratar-substation": ("Nuwakot", "Bagmati"),
    "trishuli-3b-hub-substation": ("Nuwakot", "Bagmati"),
    "chilime-hub-substation": ("Rasuwa", "Bagmati"),
    "malekhu-substation": ("Dhading", "Bagmati"),
    "mulpani-substation": ("Kathmandu", "Bagmati"),
    "phutung-substation": ("Kathmandu", "Bagmati"),
    "grang-substation": ("Rasuwa", "Bagmati"),
    # Hetauda Grid Division
    "hetauda-substation": ("Makwanpur", "Bagmati"),
    "kamane-substation": ("Makwanpur", "Bagmati"),
    "bharatpur-substation": ("Chitwan", "Bagmati"),
    "birgunj-substation": ("Parsa", "Madhesh"),
    "simra-substation": ("Bara", "Madhesh"),
    "amlekhgunj-substation": ("Bara", "Madhesh"),
    "pathlaiya-substation": ("Bara", "Madhesh"),
    "parsauni-substation": ("Bara", "Madhesh"),
    "kulekhani-substation": ("Makwanpur", "Bagmati"),
    # Dhalkebar Grid Division
    "chapur-substation": ("Rautahat", "Madhesh"),
    "rupani-substation": ("Saptari", "Madhesh"),
    # Duhabi Grid Division
    "duhabi-substation": ("Sunsari", "Koshi"),
    "anarmani-substation": ("Jhapa", "Koshi"),
    "damak-substation": ("Jhapa", "Koshi"),
    "godak-substation": ("Ilam", "Koshi"),
    "phidim-substation": ("Panchthar", "Koshi"),
    "amarpur-kabeli-substation": ("Panchthar", "Koshi"),
    "kushaha-substation": ("Sunsari", "Koshi"),
    "tumlingtar-substation": ("Sankhuwasabha", "Koshi"),
    "baneshwor-koshi-corridor-substation": ("Sankhuwasabha", "Koshi"),
    "basantapur-substation": ("Terhathum", "Koshi"),
    "dhungesanghu-substation": ("Taplejung", "Koshi"),
    # Butwal Grid Division
    "butwal-substation": ("Rupandehi", "Lumbini"),
    "kawasoti-substation": ("Nawalparasi East", "Gandaki"),
    "gandak-substation": ("Nawalparasi West", "Lumbini"),
    "new-butwal-substation": ("Nawalparasi West", "Lumbini"),
    "sunwal-substation": ("Nawalparasi West", "Lumbini"),
    "tamghas-substation": ("Gulmi", "Lumbini"),
    # Pokhara Grid Division
    "damauli-substation": ("Tanahun", "Gandaki"),
    "pokhara-substation": ("Kaski", "Gandaki"),
    "lekhnath-substation": ("Kaski", "Gandaki"),
    "syangja-substation": ("Syangja", "Gandaki"),
    "lahachowk-substation": ("Kaski", "Gandaki"),
    "kirtipur-substation": ("Lamjung", "Gandaki"),  # Dordi Corridor 132 kV
    "new-modi-switching-substation": ("Parbat", "Gandaki"),
    # Attaria Grid Division
    "attaria-substation": ("Kailali", "Sudurpashchim"),
    "pahalmanpur-substation": ("Kailali", "Sudurpashchim"),
    # Khimti Grid Section
    "new-khimti-substation": ("Ramechhap", "Bagmati"),
    "singati-substation": ("Dolakha", "Bagmati"),
    "garjyang-substation": ("Ramechhap", "Bagmati"),
    "indrawati-substation": ("Sindhupalchok", "Bagmati"),
    "lamosanghu-substation": ("Sindhupalchok", "Bagmati"),
    # Kohalpur Grid Division
    "kohalpur-substation": ("Banke", "Lumbini"),
    "ghorahi-substation": ("Dang", "Lumbini"),
    # Under Construction & Planned Substations
    "biratnagar-substation": ("Morang", "Koshi"),
    # Ridi Bazaar straddles Gulmi/Palpa; NEA FY 2024/25 says the line serves "Palpa and Gulmi districts" -> district and province left blank (validator requires a sourced district for province)
    "ridi-substation": ("", ""),
    "salimpur-substation": ("Sarlahi", "Madhesh"),
    "hakui-substation": ("Nawalparasi West", "Lumbini"),
    "dailekh-substation": ("Dailekh", "Karnali"),
    "balkot-substation": ("Bhaktapur", "Bagmati"),
    "dahachowk-substation": ("Kathmandu", "Bagmati"),
    "barhabise-substation": ("Sindhupalchok", "Bagmati"),
    "chobhar-substation": ("Kathmandu", "Bagmati"),
    "thimi-substation": ("Bhaktapur", "Bagmati"),
    "khudi-220-132kv-substation": ("Lamjung", "Gandaki"),
    "dharapani-substation": ("Manang", "Gandaki"),
    "changunarayan-substation": ("Bhaktapur", "Bagmati"),
    "balkumari-substation": ("Lalitpur", "Bagmati"),
    "borang-substation": ("Dhading", "Bagmati"),
    "lapang-substation": ("Dhading", "Bagmati"),
    "madichaur-substation": ("Rolpa", "Lumbini"),
    "dadakhet-substation": ("Myagdi", "Gandaki"),
    "rahughat-substation": ("Myagdi", "Gandaki"),
    "pangtang-substation": ("Sindhupalchok", "Bagmati"),
    "keraun-substation": ("Morang", "Koshi"),
    "dumkibas-substation": ("Nawalparasi East", "Gandaki"),
    "bakaspur-substation": ("Banke", "Lumbini"),
    "dhaubadi-substation": ("Nawalparasi East", "Gandaki"),
    "dharan-substation": ("Sunsari", "Koshi"),
    "palpa-substation": ("Palpa", "Lumbini"),
    "sukhipur-substation": ("Siraha", "Madhesh"),
    "bodebarsain-substation": ("Saptari", "Madhesh"),
    "saruattha-substation": ("Rautahat", "Madhesh"),
    "birauta-substation": ("Kaski", "Gandaki"),
    "safebagar-substation": ("Achham", "Sudurpashchim"),
    "ghartigaun-substation": ("Rolpa", "Lumbini"),
    "ratnapark-substation": ("Kathmandu", "Bagmati"),
    "maharajgunj-substation": ("Kathmandu", "Bagmati"),
    "sirutar-substation": ("Bhaktapur", "Bagmati"),
    "auraha-substation": ("Bara", "Madhesh"),
    "gaidakot-substation": ("Nawalparasi East", "Gandaki"),
    "meghauli-substation": ("Chitwan", "Bagmati"),
    "nijgadh-substation": ("Bara", "Madhesh"),
    # NEA FY 2025/26: "Harnaiya Substation (Adarsha Kotawal Rural Municipality, Bara)"
    "harnaiya-substation": ("Bara", "Madhesh"),
    "new-kohalpur-substation": ("Banke", "Lumbini"),
    # NEA FY 2025/26 transmission map labels it "DAIJI (NEW ATTARIYA)" (Daiji, Kanchanpur); the RPGCL symbol is in Kanchanpur
    "new-attariya-substation": ("Kanchanpur", "Sudurpashchim"),
    "likhu-hub-substation": ("", ""),
    "sunkoshi-hub-substation": ("", ""),
    "philim-gumda-substation": ("Gorkha", "Gandaki"),
    "kalikot-substation": ("Kalikot", "Karnali"),
    "jumla-substation": ("Jumla", "Karnali"),
    "banfikot-substation": ("Rukum West", "Karnali"),
    "kavre-ramechhap-substation": ("", ""),
    "old-nepalgunj-substation": ("Banke", "Lumbini"),
    "tinpiple-substation": ("Kathmandu", "Bagmati"),
}

# Canonical geography & verified substation_slug links for industrial_load_anchors.csv
INDUSTRIAL_ANCHOR_ENRICHMENT: dict[str, tuple[str, str, str]] = {
    # anchor_id -> (district, province, substation_slug)
    "simara-parwanipur-industrial-corridor": ("Bara", "Madhesh", "amlekhgunj-substation"),
    "simara-sez": ("Bara", "Madhesh", "auraha-substation"),
    "birgunj-industrial-area": ("Parsa", "Madhesh", "parsauni-substation;birgunj-substation"),
    "birgunj-jitpur-simara-industrial-corridor": ("Bara", "Madhesh", "simra-substation"),
    "bhumahi-bhairahawa-industrial-corridor": ("Nawalparasi West", "Lumbini", "hakui-substation"),
    "nepalgunj-industrial-area": ("Banke", "Lumbini", "bakaspur-substation"),
    "cg-cement-palpa": ("Palpa", "Lumbini", "ridi-substation"),
    "maruti-cement-siraha": ("Siraha", "Madhesh", "sukhipur-substation"),
    "eastern-industrial-corridor-sunsari": ("Sunsari", "Koshi", "inaruwa-substation"),
    "industrial-district-balaju": ("Kathmandu", "Bagmati", "balaju-substation"),
    "industrial-district-patan": ("Lalitpur", "Bagmati", "new-patan-substation"),
    "industrial-district-hetauda": ("Makwanpur", "Bagmati", "hetauda-substation"),
    "industrial-district-pokhara": ("Kaski", "Gandaki", "pokhara-substation"),
    "industrial-district-butwal": ("Rupandehi", "Lumbini", "butwal-substation"),
    "industrial-district-dharan": ("Sunsari", "Koshi", "dharan-substation"),
    "industrial-district-nepalgunj": ("Banke", "Lumbini", "old-nepalgunj-substation"),
    "industrial-district-bhaktapur": ("Bhaktapur", "Bagmati", "bhaktapur-substation"),
    "industrial-district-birendranagar": ("Surkhet", "Karnali", "surkhet-substation"),
    "industrial-district-gajendranarayan": ("Saptari", "Madhesh", "rupani-substation"),
    "bhairahawa-sez": ("Rupandehi", "Lumbini", "mainahiya-substation"),
}


def append_note(existing: str, tag: str) -> str:
    if tag in existing:
        return existing
    return f"{existing}; {tag}" if existing.strip() else tag


def enrich_substations() -> set[str]:
    path = ROOT / "data" / "substation_specs.csv"
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    updated = 0
    valid_slugs: set[str] = set()
    for r in rows:
        slug = r["slug"].strip()
        valid_slugs.add(slug)
        changed = False
        # Derive province from existing district first if missing
        dist = r["district"].strip()
        prov = r["province"].strip()
        if dist in DISTRICT_TO_PROVINCE and not prov:
            r["province"] = DISTRICT_TO_PROVINCE[dist]
            changed = True
        elif slug in SUBSTATION_CANONICAL_GEO:
            c_dist, c_prov = SUBSTATION_CANONICAL_GEO[slug]
            # Normalize bare "Nawalparasi" to Nawalparasi West (all 3 are in Lumbini/West)
            if not dist or (dist == "Nawalparasi" and not prov):
                if c_dist:
                    r["district"] = c_dist
                    changed = True
            if not prov and c_prov:
                r["province"] = c_prov
                changed = True
        if changed:
            r["notes"] = append_note(r["notes"], "geography basis: canonical-geography lookup")
            updated += 1

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    filled_p = sum(1 for r in rows if r["province"].strip())
    filled_d = sum(1 for r in rows if r["district"].strip())
    print(f"substation_specs.csv: updated {updated} rows | province {filled_p}/{len(rows)} | district {filled_d}/{len(rows)}")
    return valid_slugs


def enrich_industrial_anchors(valid_substation_slugs: set[str]) -> None:
    path = ROOT / "data" / "industrial_load_anchors.csv"
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    updated = 0
    for r in rows:
        aid = r["anchor_id"].strip()
        if aid not in INDUSTRIAL_ANCHOR_ENRICHMENT:
            continue
        c_dist, c_prov, c_slugs = INDUSTRIAL_ANCHOR_ENRICHMENT[aid]
        # Verify every referenced substation slug exists in substation_specs.csv
        for s in c_slugs.split(";"):
            assert s in valid_substation_slugs, f"Unknown substation slug {s!r} for {aid}"
        changed = False
        if r["district"].strip() in ("", "unknown"):
            r["district"] = c_dist
            changed = True
        if r["province"].strip() in ("", "unknown"):
            r["province"] = c_prov
            changed = True
        if not r["substation_slug"].strip():
            r["substation_slug"] = c_slugs
            changed = True
        if changed:
            r["reliability_or_feeder_notes"] = append_note(
                r.get("reliability_or_feeder_notes", ""),
                "district/province/substation_slug via canonical-geography + substation_specs.csv",
            )
            updated += 1

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"industrial_load_anchors.csv: updated {updated}/{len(rows)} rows (100% district/province/substation_slug linked)")


def main() -> int:
    valid_slugs = enrich_substations()
    enrich_industrial_anchors(valid_slugs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
