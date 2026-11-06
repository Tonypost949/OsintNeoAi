# Internment evidence package — Yamada / Hamada / Huntington Beach

Assembled 2026-11-06 for the RULE-2026-10 Test Case #1 follow-through pulls
(Tonypost949/ailaws). Everything here is a primary record or a report that
names its primary records. Statements in the reports are DOCUMENTED (document
named) or NOT YET DOCUMENTED (settling pull named) — nothing else.

## reports/
- TERMINAL_KMC_PULL_RESEARCH.md — Terminal Island first removal (Navy 48-hour
  notice, Feb 25, 1942), EO 9066 / curfew / 5-mile-limit paper trail, KMC =
  Kilauea Military Camp (Hawaii), Civilian Exclusion Order No. 61 (Orange
  County, control station Huntington Beach, removal to Poston).
- YAMADA_NAME_SEARCH.md — NARA Form 26 master file + FAR + Densho searches:
  Mitsuru Yamada (b.1934) documented at Poston, Family 21270; two Shigeru
  Yamada b.1928 candidates (21270 Imperial Co. / 24045 Santa Ana); the real
  HAMADA family of Huntington Beach / Orange County; Hisako Hamada b.1922
  (Santa Ana, Poston); Hisako Yamada b.1923 NOT FOUND in any index searched.
- IREIZO_NAME_SEARCH.md — Ireizo (JANM/USC) searched live; Family 21270
  confirmed Poston + Tule Lake; Hamada family Jerome/Tule Lake.
- YAMADA_FAMILY_21270_ROSTER.md — the nine members of Family 21270 (Imperial
  Valley; Holtville -> Poston 1942-05-21 -> Tule Lake 1943-10-07) and the
  Santa Ana Family 24045.
- HB_FAR_POSTON_ROSTER.md — all 105 Huntington Beach people (26 families) on
  the Poston roster, entered May 15-17, 1942. No Yamada, no Hamada on it.
- AREA_AND_TULELAKE_RESULTS.md — city-level physical-area search method and
  the Tule Lake transcription records for Family 21270.
- TULELAKE_FAR_AND_1940ED.md — original Tule Lake FAR series located (NAID
  1055789, microfilm M1865 Roll 10); 1940 census ED framework for Orange
  County (Liberty Park ED not yet determined); A. B. Anderson NOT FOUND.
- FAMILY_NUMBER_CHECK_17631_17642.md — 17631/17642 are BOTH the Cameron Lane /
  Beach Blvd parcel addresses AND real WRA family numbers (17631 = Iwasa,
  17642 = Izumi, both Seattle -> Minidoka). Coincidence documented as such.

## data/
The full datasets the searches ran on: wra-master.csv (complete NARA WRA
internee file, 109,212 rows; in data/parts/ as plain split parts),
far-poston.csv, far-manzanar.csv, far-minidoka.csv (Densho Names Registry
FAR transcriptions).

## originals/
Full-size original records, byte-identical to the Internet Archive items
(densho-nr-far-tulelake, densho-nr-far-poston):
- nr-far-tulelake.pdf — Tule Lake Final Accountability Roster, March 1946,
  615 pages, 677,533,878 bytes — in originals/parts/ as base64 split parts.
- nr-far-poston.pdf — Poston Final Accountability Roster, 418 pages,
  555,399,116 bytes — in originals/parts/ as base64 split parts.
- nr-far-tulelake_jp2.zip — the Tule Lake roster's original page images
  (JPEG 2000), 412,178,978 bytes — in originals/parts/ as base64 split parts.
- OCR layers for both rosters (djvu.txt whole; djvu.xml in plain split parts).
- civil-exclusion-order-61_csudh.pdf.b64 and public-proclamation-3_csudh.pdf
  .b64 — the two CSUDH primary orders (decode with base64 -d).
- civil-restrictive-order-1_berkeley.pdf — Civilian Restrictive Order No. 1
  (in originals/parts/ as base64 split parts).
- 13_Westminster_Road_District_1912_Plat.jpg — the 1912 Westminster Road
  District ownership plat of Wintersburg (owner name + acreage per parcel),
  from the user's own Google Drive; Orange County Archives original.
- SHA256SUMS.txt — hashes of every whole original. PARTS_SHA256SUMS.txt —
  hashes of every stored part file. Files are stored split because the
  GitHub connector path accepts text only, in limited-size snapshots:
  plain-text sources are split raw (cat <name>.part-* > <name>); binary
  sources were base64-encoded first, then split (cat <name>.b64.part-* |
  base64 -d > <name>). Either way, verify the rebuilt file against
  SHA256SUMS.txt. The split sets were verified end-to-end on 2026-11-06:
  every rebuilt original's SHA-256 matches its whole-file hash above.
- drive_finds/ — the user's own Drive copies: the 1912 plat, the VAR1996012
  title package (labels + assessor maps incl. Tract 411 / P.M. 112-48), the
  UVX536 (1963) labels, and OCR text of the UPX1977055 / UPX1977008 /
  DRB2006039 label sets. See reports/DRIVE_FINDS_LABELS_PLAT_WELLS.md.

## Named gaps (not conclusions)
- (Closed 2026-11-06) Civilian Exclusion Order No. 61 and Public
  Proclamation No. 3 PDFs (CSUDH): in originals/ as .b64 files, downloaded
  via the browser route after the direct route failed; hashes in
  originals/SHA256SUMS.txt.
- Post-Tule Lake destinations for Family 21270: the original roster pages
  must be read visually; the OCR text layer cannot carry the table.
- 1940 census ED for Liberty Park (Beach/Cameron/Speer): candidates
  30-48 / 30-46 / 30-49; settling sources are the NARA ED descriptions
  (T1224) and ED maps (A3378).
