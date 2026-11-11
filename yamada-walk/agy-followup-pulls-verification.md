# AGY FOLLOW-UP PULLS — 2026-11-10

Four public, internet-only verification pulls arising from review of the AI-generated (agy) Yamada dossier.
No purchases, no orders, no contact with any custodian or person. Public index/database reads and web searches only.
Method note: several of the target systems (RecorderWorks, NARA AAD search results, BLM GLO, GeoTracker, CSUMB PDF downloads) are interactive/JavaScript or returned 403 to the text fetcher used here. Where a pull could not be completed through that route, it is graded NOT YET DOCUMENTED and the exact settling pull is named. A fetch failure is a tool limitation, not evidence the record does not exist.

---

## 1. Orange County RecorderWorks — Cameron deed instrument variants + Beach deed

**Grade: NOT YET DOCUMENTED (RecorderWorks index itself not read); the two transactions are corroborated in other public records (below).**

What was tried:
- RecorderWorks portal opened: https://cr.occlerkrecorder.gov/RecorderWorksInternet/ — the Grantor/Grantee index (documents recorded since 1982) is an interactive form application (Search by Name / Search By Document Number / Search By Book and Page / Search By Recording Date / Search By Document Type). The text fetcher can read the portal page but cannot submit the document-number search form, so neither instrument variant could be run against the index itself in this pass.
- Exact-number web searches for "202000420412" and "202100002954" returned no Orange County index entries (RecorderWorks results are not web-indexed; the "202100002954" hits were unrelated instruments in Ohio/Indiana/Arkansas counties that reuse the same number format).

Format observation (analysis, not an index read): Orange County instrument numbers are 12 digits — a 4-digit year plus an 8-digit sequence.
- 202000420412 = 2020 + 00420412 — fits the format.
- 2020000420412 = 13 digits (2020 + 000420412) — carries an extra zero and does not fit the county's 12-digit format; on format alone it is the malformed variant.
- 202100002954 = 2021 + 00002954 — fits the format.
This makes 202000420412 the structurally valid candidate, but which variant the RecorderWorks index actually holds was NOT confirmed by reading the index.

Corroboration of the underlying transactions from public records:
- City of Huntington Beach Housing Successor Annual Report (SB 341), FY 2024/25 — table lists "17631 Cameron Lane" with date 8/19/2020: Housing Authority PSA dated 3/16/2020 to purchase for $3,041,669 ($50,000 deposit paid FY 2019/20), closed escrow early FY 2020/21, now the Navigation Center site; and "17642 Beach Blvd" with date 01/05/2021. Source: https://cms3.revize.com/revize/huntingtonbeachca/Documents/Departments/Community%20Development/Affordable%20Housing/Successor%20Agency/SB%20341%20Report%20-%20FY%202024-25%20-%20Final.pdf
- Bisnow, Feb 24, 2020: council voted to acquire 17631 Cameron Lane "from the Shigeru Yamada Living Trust and Mitsuru Yamada Living Trust for $3.1M. CBRE is representing the city and the family trusts"; the adjoining 17642 Beach Blvd parcel, "also owned by the Yamada trust," under option at a similar price. Source: https://www.bisnow.com/news/orange-county/affordable-housing/a-year-after-state-sues-huntington-beach-gives-the-go-ahead-to-buy-land-for-affordable-housing-103103
- The 8/19/2020 (Cameron) and 01/05/2021 (Beach) dates in the SB 341 table match the recording dates carried in our in-hand file for instruments 202000420412 and 202100002954 respectively. No grantor-name variants from the Recorder's index itself were obtained.

Settling pull (named, not run): a live interactive RecorderWorks session — Search By Document Number for 202000420412, 2020000420412, and 202100002954, plus a Search by Name under YAMADA MITSURU TR / YAMADA SHIGERU TR — which returns grantors, grantee, document type, and recording date for each hit.

---

## 2. NARA AAD — Japanese-American Internee File: family number 21270 or 24002?

**Grade: series DOCUMENTED; the brothers' individual records and the family number NOT YET DOCUMENTED from the official record in this run. Nothing found in this run supports 24002.**

What was documented:
- The series exists as described: "Records About Japanese Americans Relocated During World War II," Record Group 210 (Records of the War Relocation Authority), National Archives Identifier 574045; single file unit "[Japanese-American Internee Data File], 1942–1946," NAID 1264228, 109,377 records in AAD (109,384 per the file's technical documentation), built from WRA Form 26 punch-card data. Source: https://aad.archives.gov/aad/series-description.jsp?s=623
- AAD's internal file code for this file unit is dt=3099 (visible in AAD record-detail URLs for this file, e.g. a sample Ogawa record: aad.archives.gov/aad/record-detail.jsp?dt=3099&…&q=Ogawa).

What was tried for the individual records:
- AAD partial-records search URL for "Mitsuru Yamada" (dt=3099) — returned HTTP 403 to the text fetcher; the search could not be executed through this route.
- Densho Names Registry (https://ddr.densho.org/names/) — the searchable public mirror of the same NARA WRA-26 data plus the Final Accountability Rosters; it is form-driven, and no indexed person page for Mitsuru or Shigeru Yamada surfaced in web searches.
- Web searches on both names with camp/family-number terms returned no internee-record hit for either brother.

Identity corroboration (does not carry the family number): California Birth Index — Mitsuru Yamada, born 02/24/1934, Imperial County, mother's maiden name Okada; listed potential siblings include Shigeru (born 1928) and Fusaye (born 1931) — consistent with the composition of the family in our in-hand documents. Source: https://californiabirthindex.org/birth/mitsuru_yamada_born_1934_1727418

Bottom line on the question asked: our in-hand documents carry Family 21270 (Mitsuru documented as Poston Family 21270 / Individual 21270I; Tule Lake ledger pp. 551–555). No source found in this run shows 24002 attached to this family, and no official-record pull in this run shows either number. The agy dossier's 24002 is therefore unsupported by anything found here, but it is not yet contradicted by the AAD record itself, which remains unread.

Settling pulls (named, not run): (1) live AAD fielded search, dt=3099, on YAMADA MITSURU (b. 1934) and YAMADA SHIGERU (b. 1928) — the record's fields include LAST NAME, INDIVIDUAL NUMBER, and FILE NUMBER; (2) Densho Names Registry search on both names, which displays the WRA-26 "Family No." directly; (3) the Tule Lake Final Accountability Roster (March 1946) Yamada entries, which list family number per person.

---

## 3. "DTSC document number" 2017000109919

**Grade: NOT FOUND as a DTSC document in any public index searched.**

What was tried:
- Exact-number web search "2017000109919" — no DTSC or EnviroStor hit. The only exact match anywhere was an unrelated Adams County, Colorado property report, where 2017000109919 appears as a 12/13/2017 warranty-deed reception number (Brighton, CO) — a different state and system.
- Context searches (DTSC document + Cameron/Beach covenant; GeoTracker T10000018579 covenant) returned no document bearing this number. The GeoTracker profile page for T10000018579 (https://geotracker.waterboards.ca.gov/profile_report?global_id=T10000018579) returned HTTP 403 to the text fetcher, and DTSC EnviroStor's search is form-driven, so neither system's internal document list could be read directly in this pass.

Format observation (labeled inference, not a find): 2017000109919 parses as 2017 + 000109919 — the Orange County Recorder's 12-digit instrument format (compare 202000420412 and 202100002954 in Pull 1), not the format of an EnviroStor document ID. If this number resolves anywhere, the most likely home for it is a 2017 instrument in the OC Recorder's index, misattributed to DTSC somewhere along the chain. That is an inference from the number's shape only; the instrument itself was not read.

Settling pulls (named, not run): (1) RecorderWorks Search By Document Number for 2017000109919 — if it hits, the index entry gives document type, grantors/grantee, and recording date, which would identify the covenant (or whatever the instrument is) directly; (2) the document list on the GeoTracker case page for T10000018579 / T10000020555 in a live browser session; (3) EnviroStor name/address search for 17631 Cameron Ln / 17642 Beach Blvd in a live session.

---

## 4. BLM GLO — accessions CA0750__.001 and CA0780__.042 (Rancho Las Bolsas)

**Grade: the two Las Bolsas patents are DOCUMENTED from public sources; the accession-to-patent mapping is NOT YET DOCUMENTED (GLO's own detail sheets not read).**

What was tried:
- GLO details URLs for both accessions (https://glorecords.blm.gov/details/patent.aspx?accession=CA0750__.001&docClass=SER and the same for CA0780__.042) — the GLO portal is a JavaScript application and returned only a "Loading" shell to the text fetcher; no record data.
- Exact-accession web searches returned no indexed GLO detail page for either number.
- The CSU Monterey Bay Hornbeck collection holds BLM-sourced "Land Patent Details" sheets (the printouts that carry the accession numbers) for both Las Bolsas halves, but the PDF downloads returned HTTP 403 to the text fetcher.

What is documented about the patents themselves:
- Rancho Las Bolsas — 33,460-acre 1834 Mexican land grant from the partition of Rancho Los Nietos, in present-day northwestern Orange County; original grantee Maria Catarina Ruiz (widow of José Antonio Nieto). Claims were filed with the Public Land Commission in 1852 as required by the Land Act of 1851 (Act of March 3, 1851) — that Act is the confirming authority under which both U.S. patents issued. Source: https://en.wikipedia.org/wiki/Rancho_Las_Bolsas
- Patent 1 — issued June 19, 1874, to Ramon Yorba and others, for an undivided half of Rancho Las Bolsas. Stated in Harrison v. Ulrichs, 39 F.1d 654 (Circuit Court, S.D. Cal., Aug. 12, 1889): "one issued June 19, 1874, to Ramon Yorba and others." Source: https://openjurist.org/39/f1d/654
- Patent 2 — issued August 27, 1877, to Juan Jose Murillo and his wife (María Cleofa Nieto Murillo), for the other undivided half. Same case: "the other issued August 27, 1877, to Juan Jose Murillo and his wife. Both of these patents embrace the demanded premises." Source: https://openjurist.org/39/f1d/654
- BLM document set corroboration (CSUMB Hornbeck collection, BLM-sourced): "Las Bolsas [Yorba], one undivided half, Diseño 402, GLO No. 471-A" — BLM Patent dated June 19, 1874, with a BLM Land Patent Details sheet; "Las Bolsas [Nieto], one undivided half, Diseño 459, GLO No. 471-B" — BLM Patent dated Aug. 27, 1877, with a BLM Land Patent Details sheet. Sources: https://digitalcommons.csumb.edu/hornbeck_usa_4_a_oc/8/ and https://digitalcommons.csumb.edu/hornbeck_usa_4_a_oc/7/
- Land description as documented: each patent covers an undivided one-half interest in the whole Rancho Las Bolsas tract (33,460 acres) as surveyed — not a township/range/section aliquot description; rancho patents issue on the confirmed grant's surveyed boundaries (Diseño 402 for the Yorba half; Diseño 459 for the Nieto/Murillo half). Note one discrepancy in the secondary record only: the Wikipedia infobox line says Yorba was "patented half … in 1872," while the court record and the BLM patent document both date the Yorba patent June 19, 1874; the 1874 date is the documented one.

What is NOT documented: which accession — CA0750__.001 or CA0780__.042 — attaches to which patent. The accession numbers live on the GLO detail sheets, which could not be read here (GLO portal JavaScript-only to this fetcher; CSUMB copies of the same sheets blocked at download).

Settling pulls (named, not run): (1) live GLO session at https://glorecords.blm.gov/ searching each accession — the detail page gives patentee names, issue date, total acres, land description, and the authority line for each; (2) the two "BLM Land Patent Details" PDFs (115 KB each) in the CSUMB Hornbeck Las Bolsas 471-A and 471-B sets, fetched in a live browser.

---

## Summary

| # | Item | Grade |
|---|------|-------|
| 1 | RecorderWorks: 202000420412 vs 2020000420412; Beach 202100002954 | NOT YET DOCUMENTED (index not readable via text fetch; 12-digit format favors 202000420412; both transactions corroborated in SB 341 report + Bisnow) |
| 2 | NARA AAD family number: 21270 vs 24002 | Series DOCUMENTED; individual records NOT YET DOCUMENTED (AAD search 403 to fetcher; nothing found anywhere supports 24002) |
| 3 | DTSC doc 2017000109919 | NOT FOUND as a DTSC document; number is shaped like a 2017 OC Recorder instrument (inference, labeled) |
| 4 | BLM GLO CA0750__.001 / CA0780__.042 | Both Las Bolsas patents DOCUMENTED (Yorba et al., 6/19/1874; Murillo & wife, 8/27/1877; undivided halves, Land Act of 1851); accession-to-patent mapping NOT YET DOCUMENTED |

All four open items share one settling route: a live interactive browser session (RecorderWorks, AAD, GLO, GeoTracker/EnviroStor are all form/JavaScript systems that a text fetch cannot drive). No custodian was contacted and nothing was ordered.

## CORRECTION (2026-11-10 18:34 PST) — Pull 1 is now SETTLED by a live index read; the format analysis was wrong
A live RecorderWorks session after this report ran the document-number search directly: the index carries the Cameron grant deed as **2020000420412 (13 digits)** — GRANT DEED, recorded 8/19/2020, 4 pages, grantors YAMADA SHIGERU TR / YAMADA MITSURU TR / MITSURA YAMADA LIVING TRUST / SHIGERU YAMADA LIVING TRUST, grantee HUNTINGTON BEACH HOUSING AUTHORITY; the 12-digit form 202000420412 resolves to the same record. The 12-digit-format observation in Pull 1 was inference and is **withdrawn** — the county's number for this instrument is 13 digits as recorded. The dossier's instrument number was correct on this point.

## RESOLVED (2026-11-10 18:49–18:55 PST, live Densho Names Registry session): Pull 2 is SETTLED — Family 21270
The Densho Names Registry (ddr.densho.org/names) carries **WRA Family No. 21270** for Yutaka Yamada's family, for both brothers: Mitsuru (b. 1934) = 21270I across FAR Ancestry Poston, FAR Poston (Line 18379) and WRA Form 26 (File 208775); Shigeru (b. 1928) = 21270G across FAR Poston (Line 18377) and WRA Form 26 (File 208773). Family table under 21270: Yutaka 21270B, Haruye 21270A, Takashi 21270D, Yoshiye 21270E, Hiroshi 21270F, Shigeru 21270G, Fusaye 21270H, Mitsuru 21270I — matching the in-hand Tule Lake ledger record. **24002 belongs to a different Poston family — Jisuke Yamada's (Jisuke 1878, Sowa 1876, Hatsumi 1910, Michiko 1922); it never appears on Yutaka's family's records. The dossier's "Family Unit #24002" (§1.4) is WRONG, settled.** Registry wrinkle, recorded not resolved: the registry ALSO carries a Shigeru (William) Yamada, b. 1928, Poston, under Family 24045 (Fusashichi Yamada's family, individual 24045D) sharing Alternate Family ID 29444 with Mitsuru's 21270 record; the registry does not reconcile the two. The 21270 set is the one consistent with every in-hand record (family composition, Holtville, the Tule Lake ledger). Tule Lake FAR records for both men carry no WRA family number.
