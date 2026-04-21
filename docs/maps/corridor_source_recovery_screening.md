# Corridor Source Recovery Screening

Date: 2026-04-18

Purpose: initial screening of the best recovery paths for missing Nepal transmission-route documents, with emphasis on the unresolved `kabeli_132` and the already-partially-recovered Marsyangdi packet family.

## Summary

The highest-promise recovery paths are now clear:

1. `Kabeli Corridor 132 kV`: the best path is **Wayback recovery of the original NEA publication binaries**.
2. `Marsyangdi Corridor 220 kV`: the best path is **direct recovery from the live NEA dryicesolutions mirror**.
3. `EIB attachments`: strong **backup / companion source**, especially for Marsyangdi, but not the first-choice path when NEA originals are available.
4. `World Bank document-detail pages`: useful for **archival breadcrumbs and corroboration**, but weaker as a direct download path from this environment.

## Screening results

### 1. Kabeli Corridor 132 kV

Status: **strongest recovery path found**

Best source:

- Wayback snapshot of the old NEA publications page:
  - `https://web.archive.org/web/20120216232653/http://www.nea.org.np/publications.html`

What this page exposes:

- `RAP FOR ANGLE TOWERS - Kabeli TL.pdf`
- `SOCIAL IMPACT ASSESSMENT - Kabeli TL.pdf`
- `SOCIAL MANAGEMENT and ENTITLEMENT FRAMEWORK - Kabeli TL.pdf`
- `Initial Environmental Examination _IEE_ Study Vol-I of Kabeli Corridor TL Project.pdf`

The key point is that the old NEA files were under:

- `/images/supportive_docs/...`

not under:

- `/admin/assets/uploads/supportive_docs/...`

That means the old manifest path assumption was wrong for these 2011-era files.

Verified working binary recoveries:

- IEE:
  - `https://web.archive.org/web/20120216232653/http://www.nea.org.np/images/supportive_docs/Initial%20Environmental%20Examination%20_IEE_%20Study%20Vol-I%20of%20Kabeli%20Corridor%20TL%20Project.pdf`
- SMEF:
  - `https://web.archive.org/web/20120216232653/http://www.nea.org.np/images/supportive_docs/SOCIAL%20MANAGEMENT%20and%20ENTITLEMENT%20FRAMEWORK%20-%20Kabeli%20TL.pdf`

Verification notes:

- The IEE URL returned a real PDF on 2026-04-18.
- `pdfinfo` shows:
  - title: `Initial Environmental Examination _IEE_ Study Vol-I of Kabeli Corridor TL Project.doc`
  - pages: `196`
  - creation date: `2011-01-10`
- The SMEF URL returned a real PDF on 2026-04-18.
- `pdfinfo` shows:
  - title: `SMEF Kabeli TL draft.doc`
  - pages: `37`
  - creation date: `2011-01-21`

Assessment:

- This is not just a lead. It is a **working recovery path**.
- For route tracing, the IEE is likely the primary packet.
- The SMEF, SIA, and RAP should be treated as supporting corridor-definition and substation / impact-area sources.

### 2. Marsyangdi Corridor 220 kV

Status: **strong direct recovery path**

Best source:

- Live NEA dryicesolutions mirror.

Verified working PDFs:

- Udipur-Markichowk-Bharatpur RAP:
  - `https://neasite.dryicesolutions.net/uploads/shares/publication/17560727.pdf`
- Manang-Khudi-Udipur RAP:
  - `https://neasite.dryicesolutions.net/uploads/shares/publication/52182611.pdf`

Verification notes:

- `17560727.pdf` returned `HTTP 200` and a real PDF on 2026-04-18.
- `pdfinfo` shows:
  - title: `Final Updated RAP-Lower Marsyangdi_MC220kVTLP_08.29.2021`
  - pages: `109`
- `52182611.pdf` returned `HTTP 200` and a real PDF on 2026-04-18.
- `pdfinfo` shows:
  - title: `RAP for Marsyangdi Corridor_Revised Version Nov 2019+EIB edits May 2020 + Feb 2021`
  - pages: `268`

Assessment:

- This is the best source family for Marsyangdi because it is live, official, and already aligned to the corridor work.
- These are strong route-grade / corridor-grade packets for tracing support.

### 3. EIB attachments

Status: **good backup and companion source**

Verified working PDFs:

- CIA report:
  - `https://www.eib.org/attachments/registers/168770873.pdf`
- external-links sheet:
  - `https://www.eib.org/attachments/registers/169745163.pdf`

Verification notes:

- `168770873.pdf` returned `HTTP 200` and a real PDF on 2026-04-18.
- `pdfinfo` / text extraction show:
  - title block: `Cumulative Impact Assessment (CIA) of Marsyangdi Corridor (Manang-Udipur and Udipur-New Bharatpur) 220kV Transmission Line Project`
  - pages: `212`
  - date: `February, 2023`
- `169745163.pdf` returned `HTTP 200` and a real PDF on 2026-04-18.
- It is a one-page pointer sheet titled:
  - `External links to Related Documents of EIB-financed projects`
  - project: `2013-0599 - NEPAL POWER SYSTEM EXPANSION PROJECT`

Assessment:

- EIB is useful for:
  - newer companion studies
  - route context
  - validating document families
- EIB is not the first-choice source when the NEA original packet is recoverable.

### 4. World Bank archives

Status: **mixed direct-download reliability, but useful archival corroboration**

Useful evidence:

- Search results and archival PDFs confirm the old NEA publication names and timing.
- The Inspection Panel PDF below reproduces the old NEA publications page and explicitly lists the Kabeli document set:
  - `https://documents1.worldbank.org/curated/en/286091468178184975/pdf/81845-IPR-P043311-Box391456B-PUBLIC-disclosed-6-5-15-INSP-R2013-0009-lPN-REQUEST-RQ-13-05.pdf`

Assessment:

- Good for breadcrumbing and corroboration.
- Less reliable than Wayback or the NEA mirror as a direct binary retrieval route in this environment.

## Ranking

### Kabeli

1. Wayback recovery of old NEA publication binaries
2. World Bank archival material as corroboration / breadcrumb source
3. Live NEA dryicesolutions site search, only as a secondary sweep
4. Old `nea.org.np/admin/...` supportive-doc URLs, which are currently blocked / rejected

### Marsyangdi

1. Live NEA dryicesolutions publication PDFs
2. EIB attachments and companion studies
3. Older NEA URLs only if needed for missing variants

## Current repo state

The immediate recovery work has now been completed in the repo:

1. the working Kabeli Wayback URLs were added to the corridor source manifest
2. the recovered Kabeli IEE / SMEF packets were downloaded into `data/raw/corridor_tracing/nea/`
3. the Marsyangdi lower and upper RAP packets and the EIB CIA packet were also archived locally
4. all recovered PDFs were indexed page-by-page under `data/processed/corridor_tracing/manifests/`
5. the Kabeli IEE is now the primary route-grade source for `kabeli_132`

The next tracing step is narrower:

1. digitize `kabeli_132` from the recovered IEE packet, starting with the figure sequence around pages `25-27`
2. use the indexed upper Marsyangdi RAP to add `marsyangdi_upper_220` to the traced corridor layer
3. leave Solu for a later source-recovery pass

## Important note

The early Kabeli documents are recoverable from the archived NEA path under `/images/supportive_docs/`, not from the later `/admin/assets/uploads/supportive_docs/` convention. That distinction is what unlocked the recovery.
