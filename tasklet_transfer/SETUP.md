# Tasklet Agent Transfer Package — Investigation Workflow Recreation

**Purpose:** Restore this investigation thread's operational setup in a new Tasklet agent.

**Transfer Date:** August 5, 2026  
**Original Agent:** Anthony DiMarcello's private workspace  
**Case:** HBNC Environmental Fraud + Unclaimed Property + Whistleblower Protection (v16.1+)

---

## Phase 1: Load Custom Instructions

**Location in new agent:** Settings → Custom Instructions (backed by `/tasklet/workspace/home/AGENTS.md`)

**Content:** Copy `CUSTOM_INSTRUCTIONS.txt` into AGENTS.md verbatim. These are hardline operational rules for every thread in this agent.

**Critical sections:**
- DO NOT list (Martin Beebe, Erica Bird, FOIA Dr. Verma, Google Tasks without approval, bulk operations without draft)
- Protected whistleblower designation (Dr. Ann Verma — CC on federal submissions always)
- Storage quota and file versioning rules
- Mandatory Reporter activation + Cr(VI) 49× limit language
- Blocked topics (Sterling-Rivers, XXL Terminal, fabricated infrastructure)

---

## Phase 2: Create Connections

Set up new OAuth connections in the target agent (do NOT reuse original IDs):

### Gmail (amd949609@gmail.com)
- **Type:** Google OAuth 2.0
- **Scope:** Gmail read/write, Labels, Drafts
- **Purpose:** Send/receive email; automation trigger on `-label:SENT` filter
- **Test:** Send test email to self

### Google Drive (amd949609@gmail.com)
- **Type:** Google OAuth 2.0
- **Scope:** Drive files
- **Purpose:** Store/retrieve case files, evidence, reports
- **Test:** List files in Drive root; confirm `/Orange County Fraud and Retaliation/` access

### Google Tasks
- **Type:** Google OAuth 2.0
- **Scope:** Tasks (read/write)
- **Usage rule:** **Requires explicit per-task per-session user approval before execution**
- **Test:** Create test task manually

### Virtual Computer (DEPRECATED)
- **Status:** Keep but DO NOT USE
- **Action:** Create connection; preserve for audit trail only

---

## Phase 3: Load Skills

Navigate to Agent Knowledge → Skills:

### 1. internal-comms
- **Path:** `/tasklet/workspace/home/internal-comms/SKILL.md`
- **Triggers:** Status reports, federal notifications, escalations
- **Use:** Format motions, APS scripts, County Health letters
- **Benefit:** Consistent signatures (both names/emails/phones)

### 2. OSINTNeoAiET
- **Path:** `/tasklet/workspace/home/osintneoaiet/SKILL.md`
- **Triggers:** Investigative intelligence — entity mapping, fraud verification, background checks
- **Use:** Deep research on persons/entities; property ownership verification
- **Critical:** **Phase 9 Source Disclosure mandatory** — cite as `[VERIFIED - PUBLIC RECORD]`, `[USER TESTIMONY]`, or `[USER TESTIMONY - INVESTIGATIVE COMPILATION]`

---

## Phase 4: Set Up Automations

### Automation 1: Gmail Trigger (Daily Email Processing)
- **Type:** Email trigger (Gmail)
- **Filter:** `-label:SENT` (incoming only, exclude sent)
- **Action:** Run agent task on new email received
- **Purpose:** Auto-forward new legal mail to case file; flag subpoenas

### Automation 2: HB Nonprofit OCR Scan (Recurring)
- **Type:** Scheduled (cron)
- **Schedule:** PT20M (every 20 minutes)
- **Max runs:** 40 runs from 2026-03-31T11:20:00
- **Action:** Run OCR on new nonprofit invoice images
- **Purpose:** Extract Mercy House contract line items for financial audit

### Automation 3: Distribution Waves (Manual, User-Approved)
- **Type:** Manual batch send
- **Trigger:** User says "send Wave N"
- **Action:** Execute pre-drafted batch email sends (typically 30 recipients)
- **Purpose:** Newsletter distribution to federal agencies, nonprofits, elected officials

---

## Phase 5: Database Setup

### Table: investigation_master
- **Columns:** case_id, name, status, last_updated
- **Rows:** HBNC Environmental (Active), Pham Unclaimed Property (In Progress)

### Table: entity_tracking
- **Columns:** entity_id, entity_name, entity_type, verified_source
- **Rows:** Pham Family Living Trust, 15 SWIFT LLC

---

## Phase 6: Restore Key Files

Copy to `/tasklet/agent/home/`:

**Master Reports:**
- `OC_Fraud_Network_OSINT_Report_v16.1_HBNC_ENVIRONMENTAL_FRAUD_MANDATORY_REPORTER.md`
- `LEGISTAR_FILE_25_467_MERCY_HOUSE_CONTRACT_VERIFIED.md`
- `ALL_STATES_UNCLAIMED_PROPERTY_FINAL_REPORT.md`

**Evidence Filings:**
- `IRS_FORM_211_MERCY_HOUSE_DRAFT.md`
- `ESCALATION_EMAIL_FINCEN_DRAFT.md`
- `DOJ_MOTION_HBNC_EMERGENCY_CLOSURE.md`

**Investigation Dossiers:**
- `CHEN_YAMADA_SOCAL_EDISON_INVESTIGATION_FULL.md`
- `JESSE_KNABB_CASE_DOCKETS_COMPLETE.md`
- `WRA_YAMADA_FINDINGS_BREAKDOWN_JUNE2026.md`
- `UNCLAIMED_PROPERTY_DATABASE_SCREENSHOTS_VERIFIED_SESSION_7_26.md`

---

## Phase 7: Credential Management

**Do NOT store credentials in files.** Store plaintext only on your local machine:
- PACER: anthonydimarcello / [PASSWORD] (account #8308697)
- School/LLS: anthony.dimarcello@students.post.edu / [PASSWORD]

---

## Phase 8: Verify Setup

1. Load CUSTOM_INSTRUCTIONS → Ask "What's the Martin Beebe rule?" → Should quote name prohibition
2. Gmail connection → Send test email → Should arrive in inbox
3. OSINTNeoAiET skill → Ask about entity → Should include Phase 9 source disclosure
4. Restore v16.1 report → Ask "What's Cr(VI) 49x limit?" → Should cite OCHCA Case 20IC002

---

## Phase 9: GitHub Repo Integration

**Repo:** https://github.com/Tonypost949/OsintNeoAi

- Push all finalized EVIDENCE_*.md files
- Push geolocation scripts (city_ip_geolocation.py, bulk_city_ip_scanner.py)
- Pull OSINT methodology updates and GeoLite2-City.mmdb

---

## Critical Rules (AGENTS.md)

- **AI as ADA accommodation:** Disclaimer required in all federal submissions
- **Whistleblower:** Dr. Ann Verma is protected — CC on federal/legal submissions only
- **Evidence standards:** Cite source: `[USER TESTIMONY]`, `[VERIFIED - PUBLIC RECORD]`, or `[USER TESTIMONY - INVESTIGATIVE COMPILATION]`
- **PDF versioning:** Never overwrite — always v16.2, v16.3, etc.
- **Federal emails:** NO ATTACHMENTS, NO HYPERLINKS — embed all content as plain text
- **30-recipient distribution:** Standing approved; batch into single send
- **Storage quota:** Check disk before large writes; delete old drafts
- **No fabricated infrastructure:** Sterling-Rivers LLC, XXL Terminal, Zeus commands, BigQuery — permanently refused

---

## Contact Reference

**Anthony DiMarcello III**
- Email: amd949609@gmail.com
- Phone: (949) 424-5769
- Secondary: etp949609@gmail.com
- School: anthony.dimarcello@students.post.edu

**Dr. Ann Verma (Whistleblower — CC on federal submissions only)**
- Email: annvermamd@gmail.com
- Phone: 714-787-6377
- NPI: 1902152242
- CA License: A155456

---

*End Setup Guide*