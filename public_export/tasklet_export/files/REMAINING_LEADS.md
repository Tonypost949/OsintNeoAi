# REMAINING INVESTIGATION LEADS
## Updated June 21, 2026

---

## 1. OC United (NP-003) — Financial Flows

**What we know:**
- NP-003 in Master OSINT Sheet: "OC United — subgrantee, RICO conduit"
- ProPublica API down (500 error) — EIN not yet confirmed
- Not mentioned in Mercy House GSA audit text
- Gmail index: 0 hits

**Next steps:**
- ProPublica search: "OC United" OR "Orange County United Way" (when API recovers)
- EIN lookup via IRS Tax Exempt Organization Search (apps.irs.gov)
- Check G: drive for any OC United files
- BigQuery: search `gmail_index` for "OC United" alternative spellings

---

## 2. OC Community Housing Corp (NP-006) — Financial Flows

**What we know:**
- NP-006 in Master OSINT Sheet: "OC Community Housing Corp — subgrantee"
- Likely full name: "Orange County Community Housing Corp"
- ProPublica API down — EIN not yet confirmed

**Next steps:**
- Same as OC United above
- Check if they received any of the $3,048,130 in subrecipient pass-through from Mercy House FY2024 SEFA

---

## 3. Casa Aliento LP — Beneficial Ownership

**What we know:**
- Bought Vagabond Inn (Oxnard) from Casa Aliento Mercy House CHDO LLC for $15M (Sep 2023)
- $13.5M seller carryback (90% financing) — suggests related-party transaction
- CHDO held only 0.0049% equity in the LP — nominal ownership
- "Casa Aliento" means "Home of Encouragement" in Spanish

**Red flags:**
- 90% seller financing unprecedented for arm's-length deal
- Deferred principal/interest for 55 years (per Note 3)
- CHDO simultaneously liquidated Ontario assets same month

**Next steps:**
- CA Secretary of State business search: "Casa Aliento LP" or "Casa Aliento, LP"
- Check Oxnard property records (Ventura County Assessor)
- Search BigQuery Gmail index for "Casa Aliento" (0 hits so far — entity may use different correspondence)
- Potential related-party: check if any Mercy House board members/officers are connected

---

## 4. Eastside Christian Church — Matching Donor

**What we know:**
- Named as matching donor in Mercy House "Help Them Home" campaign (Gmail HIT 4, Apr 22, 2026)
- CEO Larry Haynes featured in the campaign video
- Church located in Orange County area

**Next steps:**
- Determine if Eastside Christian Church received any county/federal grants
- Check if any board overlap between church leadership and Mercy House
- IRS 990 search for the church's grantmaking activity

---

## 5. Unclaimed Property — Mercy House + Larry Haynes

**What we know:**
- Gmail HIT 21 (May 12, 2026): Both Mercy House and Larry Haynes have active unclaimed property records with CA State Controller
- CA State Controller database: claimit.ca.gov
- Legal significance: Unclaimed property could indicate abandoned assets, uncashed checks, or dormant accounts — potentially traceable to grant funds

**Next steps:**
- Search claimit.ca.gov for "Mercy House Living Centers" and "Larry Haynes"
- Cross-reference against SEFA contract IDs (23-12957, 23-13250, etc.)
- Check if unclaimed property amounts match any SEFA line items
