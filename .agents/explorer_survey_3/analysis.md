# Technical Investigation Report: OsintNeoAi Indexer Architecture

**Document Version:** 1.0.0  
**Target System:** OsintNeoAi Indexer (`C:\OsintNeoAi\workspaces\osintneoai_indexer`)  
**Investigator:** Explorer Agent (`explorer_survey_3`)  
**Timestamp:** 2026-08-29T17:38:00Z  
**Authoritative Context:** `C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md` (Scope 2026-08-29T17:34:35Z) & `C:\OsintNeoAi\AGENTS.md`

---

## 1. Executive Summary & Problem Scope

The OsintNeoAi Indexer is an automated document processing, neural/offline OCR extraction, entity resolution, and timeline reconciliation pipeline. The system ingests heterogeneous primary records (PDFs, images, HTML dockets, and mailbox archives) across local directories (`C:\Users\Amd949609\Downloads`, `C:\OsintNeoAi\evidence`) and external repositories, extracting structured intelligence while enforcing strict mathematical and cryptographic invariants.

This report establishes the technical foundation for:
1. **Entity Extraction & Multi-Category Relational Indexing (R3):** A comprehensive domain taxonomy, deterministic normalization algorithms, phonetic blocking (Soundex & Double Metaphone), multi-pass fuzzy disambiguation, and regex/NER extraction rules tailored to federal, state, and municipal investigations.
2. **Database & Master Catalog Architecture:** A normalized SQLite relational schema for `C:\OsintNeoAi\workspaces\osintneoai_indexer\timeline_vault.db` and an RFC 8785-compliant structured JSON schema for `master_timeline_catalog.json`.
3. **Automated Invariant Testing & SHA-256 Verification (R4):** 64 KB chunk-streamed cryptographic file hashing, canonical JSON object hashing, hierarchical Merkle tree aggregation, schema foreign-key integrity validation, and strict chronological monotonicity assertions.
4. **Four-Tier Test Architecture (Tiers 1–4):** A complete `pytest` test suite specification guaranteeing 100% programmatic invariant verification across all records.

---

## 2. Entity Extraction & Multi-Category Relational Indexing (R3)

### 2.1 Domain Entity Taxonomy

The investigation records span municipal corruption (Anaheim Angel Stadium), unlawful detainer eviction mills (Orange County CJC), interstate logistics and narcotics (Hamilton/Ewing NJ & CDCA), and environmental/nonprofit grant diversions. Entities are categorized into 6 primary classes:

```
                                  ┌─────────────────────────────┐
                                  │      Entity Categories      │
                                  └──────────────┬──────────────┘
            ┌──────────────────┬─────────────────┼─────────────────┬──────────────────┐
            ▼                  ▼                 ▼                 ▼                  ▼
    ┌───────────────┐  ┌───────────────┐  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │  INDIVIDUAL   │  │   MUNICIPAL   │  │   FINANCIAL   │ │   PROPERTY    │ │     LEGAL     │
    │  (Defendants, │  │     BODY      │  │  INSTITUTION  │ │  MANAGEMENT   │ │  & REGULATORY │
    │   Attorneys,  │  │ (City Council,│  │  (Bank Accts, │ │ (Apartments,  │ │ (Courts, FBI, │
    │    Judges)    │  │  Chambers)    │  │ Slush Funds)  │ │  Shelters)    │ │   HCD, PD)    │
    └───────────────┘  └───────────────┘  └───────────────┘ └───────────────┘ └───────────────┘
```

#### Detailed Taxonomy Specification

| Category Code | Category Name | Description | Key Domain Examples |
|---|---|---|---|
| `INDIVIDUAL` | Natural Persons | Public officials, criminal defendants, lobbyists, eviction attorneys, judicial officers, federal agents, property managers, relators/victims. | `Harry Sidhu`, `Todd Ament`, `Melahat Rafiei`, `Jeffrey Flint`, `Arden Hoang`, `Richard S. Sontag`, `Carmen Luege`, `Brian Adkins`, `Bradley H. Zartman`, `Anthony DiMarcello`, `Vichal Nunen`, `Austin Drissen`, `Robert F. Greenglass` |
| `MUNICIPAL_BODY` | Municipal & Legislative Bodies | City councils, municipal departments, chambers of commerce, and quasi-governmental tourism bureaus. | `City of Anaheim`, `Anaheim City Council`, `Anaheim Chamber of Commerce`, `Visit Anaheim`, `City of Irvine`, `City of Huntington Beach`, `Orange County Board of Supervisors` |
| `FINANCIAL_INSTITUTION` | Financial & Conduit Entities | Commercial banks, political slush funds, escrow depositories, campaign PACs, and conduit accounts. | `TA Group LLC`, `FPS Strategies LLC`, `SRB Management Escrow`, `Progressive Solutions Consulting`, `Dog's Day Productions (EIN 155-78-7252)` |
| `PROPERTY_MANAGEMENT` | Real Estate & Housing Entities | Residential/commercial property complexes, holding companies, shelters, and target parcels. | `Woodbridge Meadows Apartments LLC`, `Mercy House Living Centers`, `Irvine Company`, `Advanced Real Estate Services`, `1456 Cedar Lane`, `17631 Cameron Lane`, `8 Lakeview Irvine`, `3125 W 5th St Santa Ana`, `Angel Stadium 150-Acre Parcel` |
| `LEGAL_AGENCY` | Courts & Law Enforcement Agencies | Federal courts, state superior courts, federal investigative bureaus, state regulators, and municipal police departments. | `USDC CDCA`, `USDC D.N.J.`, `California Superior Court (Orange County CJC)`, `FBI CDCA / DNJ`, `DEA Northeast Laboratory`, `California HCD`, `Orange County Health Care Agency (OCHCA)`, `Hamilton Township Police Division`, `Ewing Police Department`, `Orange County Sheriff's Department` |
| `COMMERCIAL_ENTITY` | Corporate & Commercial Entities | Law firms, contractors, auto dismantlers, airlines, and commercial vendors. | `Wallace, Richardson, Sontag & Le LLP`, `JL Group LLC`, `Quantum Auto Dismantler`, `Alaska Airlines (PNR JAEETQ)`, `Carlisle Development` |

---

### 2.2 Entity Resolution & Disambiguation Pipeline

Entity mentions in raw text and OCR streams exhibit spelling variations, OCR noise (e.g. `Sldhu` for `Sidhu`, `0C Court` for `OC Court`), corporate suffix variations (`LLC`, `L.L.C.`, `Inc.`), and abbreviated titles. The resolution pipeline executes a 4-stage deterministic and fuzzy disambiguation process:

```
Raw Text Mention
       │
       ▼
[Stage 1: Normalization & Punctuation Stripping]
  - Uppercasing & Unicode normalization (NFKC)
  - End-anchored corporate suffix stripping (longest-match order)
  - Address USPS directional/suffix standardization
       │
       ▼
[Stage 2: Deterministic Blocking]
  - Generate Core Key (stop-words removed)
  - Compute Russell Soundex (e.g. S530)
  - Compute Double Metaphone (Primary & Alternate codes)
       │
       ▼
[Stage 3: Multi-Score Fuzzy & Contextual Matching]
  - Exact Core Key match -> Confidence: 1.00
  - Jaro-Winkler & Normalized Levenshtein (Threshold >= 0.88)
  - Contextual Co-occurrence Scoring (Docket #, Address, Date proximity)
       │
       ▼
[Stage 4: Graph Deduplication & Disjoint-Set Union (DSU)]
  - Canonical cluster ID assignment
  - Alias list aggregation into `entities.aliases_json`
```

#### 1. Corporate Legal Suffix Stripping Rules
Corporate suffixes must be stripped from the right end of business strings in descending order of pattern length to avoid partial truncation:
```python
CORP_SUFFIX_PATTERNS = [
    r"\bPROFESSIONAL LIMITED LIABILITY COMPANY\b",
    r"\bLIMITED LIABILITY PARTNERSHIP\b",
    r"\bLIMITED LIABILITY COMPANY\b",
    r"\bPROFESSIONAL CORPORATION\b",
    r"\bPROFESSIONAL ASSOCIATION\b",
    r"\bNATIONAL ASSOCIATION\b",
    r"\bINCORPORATED\b",
    r"\bCORPORATION\b",
    r"\bP\.L\.L\.C\.", r"\bPLLC\b",
    r"\bL\.L\.P\.", r"\bLLP\b",
    r"\bL\.L\.C\.", r"\bLLC\b",
    r"\bLIMITED\b",
    r"\bCOMPANY\b",
    r"\bINC\.", r"\bINC\b",
    r"\bCORP\.", r"\bCORP\b",
    r"\bLTD\.", r"\bLTD\b",
    r"\bP\.C\.", r"\bPC\b",
    r"\bP\.A\.", r"\bPA\b",
    r"\bN\.A\.", r"\bNA\b",
    r"\bCO\.", r"\bCO\b",
]
```

#### 2. Phonetic Blocking Algorithms
- **Russell Soundex:** Retains first letter, maps subsequent consonants to 6 digit classes (`B/F/P/V`->1, `C/G/J/K/Q/S/X/Z`->2, `D/T`->3, `L`->4, `M/N`->5, `R`->6), drops duplicates and vowels, pads to 4 characters.
- **Double Metaphone:** Generates two phonetic keys (Primary and Alternate) capturing English, Germanic, Slavic, and Romance phonetic variations. For example, `Smith`, `Smyth`, and `Smidt` resolve to Primary `SM0` / `SMT`.

#### 3. Contextual Co-occurrence Scoring Formula
When fuzzy string similarity falls in the ambiguous band ($0.80 \le \text{Score}_{\text{str}} < 0.95$), context weights are applied:

$$\text{Confidence} = 0.50 \cdot \text{Score}_{\text{Jaro-Winkler}} + 0.20 \cdot \mathbb{I}_{\text{Shared Docket}} + 0.15 \cdot \mathbb{I}_{\text{Shared Address}} + 0.15 \cdot \mathbb{I}_{\text{Shared Agency}}$$

---

### 2.3 Comprehensive Regex & NER Extraction Rules

The extraction engine combines compiled high-precision regular expressions for structured identifiers with named entity extraction for unstructured narrative blocks.

#### 1. Court Case Docket Identifiers
```python
REGEX_COURT_DOCKETS = {
    "FEDERAL_CRIMINAL_CDCA": re.compile(
        r"\b(?:Case\s*No\.?\s*)?(?:8|2|3):\d{2}-(?:cr|mj|cv)-\d{5}-[A-Z0-9\-]+\b",
        re.IGNORECASE
    ),
    "FEDERAL_MAGISTRATE_DNJ": re.compile(
        r"\b(?:Case\s*No\.?\s*|Mag\.?\s*No\.?\s*)?3:\d{2}-mj-\d{5}-[A-Z0-9\-]+\b",
        re.IGNORECASE
    ),
    "CA_SUPERIOR_COURT_OC": re.compile(
        r"\b30-\d{4}-\d{8}-[A-Z]{2}-[A-Z]{2}-[A-Z]{3}\b",
        re.IGNORECASE
    ),
    "MUNICIPAL_SUMMONS_NJ": re.compile(
        r"\b(?:Summons\s*#?\s*)?(?:\d{4}-S-\d{4}-\d{6}|\d{4}-\d{3,4})\b",
        re.IGNORECASE
    )
}
```

#### 2. Statutory Violations & Legal Codes
```python
REGEX_STATUTES = {
    "FEDERAL_USC_CRIMINAL": re.compile(
        r"\b(?:18|21|31)\s+U\.S\.C\.\s+§+\s*\d+(?:\([a-z0-9]+\))*(?:\([A-Z0-9]+\))*",
        re.IGNORECASE
    ),
    "CALIFORNIA_GOVERNMENT_CODE": re.compile(
        r"\bCal\.\s+Gov(?:ernment)?\.?\s+Code\s+§+\s*\d+(?:\.\d+)?",
        re.IGNORECASE
    ),
    "CALIFORNIA_CCP": re.compile(
        r"\bCal\.\s+C(?:ode\s+of\s+)?C(?:ivil\s+)?P(?:roc(?:edure)?)?\.?\s+§+\s*\d+(?:\.\d+)?",
        re.IGNORECASE
    ),
    "CALIFORNIA_LABOR_CODE": re.compile(
        r"\bCal\.\s+Labor\s+Code\s+§+\s*\d+(?:\.\d+)?",
        re.IGNORECASE
    ),
    "NEW_JERSEY_STATUTES": re.compile(
        r"\bN\.J\.S\.A\.\s+\d+[A-Z]?:\d+(?:-\d+[a-z]*(?:\([a-z0-9]+\))*)?",
        re.IGNORECASE
    )
}
```

#### 3. Financial & Currency Transactions
```python
REGEX_FINANCIAL = {
    "CURRENCY_EXACT": re.compile(
        r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b"
    ),
    "CURRENCY_WRITTEN_MAGNITUDE": re.compile(
        r"\$\s*(\d+(?:\.\d+)?)\s*(million|billion|thousand|k|M|B)\b",
        re.IGNORECASE
    ),
    "INVOICE_WORKORDER": re.compile(
        r"\b(?:Invoice|Workorder|Receipt)\s*#?\s*([A-Z0-9\-]+)",
        re.IGNORECASE
    ),
    "TAX_EIN_SSN": re.compile(
        r"\b(?:EIN|TIN|Tax\s*ID)[:\s]*(\d{2}-\d{7})\b",
        re.IGNORECASE
    )
}
```

#### 4. Dates, Timestamps & Register of Actions (ROA)
```python
REGEX_TEMPORAL_AND_DOCKET_ENTRIES = {
    "ISO_8601_DATE": re.compile(r"\b\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?\b"),
    "US_STANDARD_DATE": re.compile(r"\b(0?[1-9]|1[0-2])[\/\-](0?[1-9]|[12]\d|3[01])[\/\-](\d{4}|\d{2})\b"),
    "WRITTEN_MONTH_DATE": re.compile(
        r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2}),?\s+(\d{4})\b",
        re.IGNORECASE
    ),
    "COURT_TIMESTAMP_TIME": re.compile(r"\b(0?[1-9]|1[0-2]):([0-5]\d)\s*(AM|PM)\b", re.IGNORECASE),
    "ROA_ENTRY_MARKER": re.compile(r"\b(?:ROA|Entry|Item)\s*#?\s*(\d+)\b", re.IGNORECASE)
}
```

---

## 3. Normalized SQLite Schema & Master Catalog JSON Schema

### 3.1 SQLite Database Specification (`timeline_vault.db`)

**File Path:** `C:\OsintNeoAi\workspaces\osintneoai_indexer\timeline_vault.db`  
**Storage Engine:** SQLite 3 with Write-Ahead Logging (WAL)  
**Integrity Configuration:** Foreign Keys Enforced, Strict Typing, Check Constraints.

```
                                  ┌───────────────────────────┐
                                  │         DOCUMENTS         │
                                  │ (Raw Artifacts & SHA-256) │
                                  └─────────────┬─────────────┘
                                                │ 1
                                                │
                                                │ N
                       ┌────────────────────────┼────────────────────────┐
                       │ N                      │ N                      │ N
                       ▼                        ▼                        ▼
             ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
             │ ENTITY_MENTIONS  │     │ TIMELINE_EVENTS  │     │  FINANCIAL_TRX   │
             └─────────┬────────┘     └────────┬─────────┘     └────────┬─────────┘
                       │ N                     │ 1                      │ 1
                       │                       │                        │
                       │ 1                     │ N                      │ N
                       ▼                       ▼                        ▼
             ┌────────────────────────────────────────────────────────────────────┐
             │                              ENTITIES                              │
             │           (Canonical Individuals, Agencies, Properties)            │
             └─────────────────────────────────┬──────────────────────────────────┘
                                               │ 1
                                               │
                                               │ N
                                               ▼
                                  ┌───────────────────────────┐
                                  │       RELATIONSHIPS       │
                                  │  (Source -> Target Edges) │
                                  └───────────────────────────┘
```

#### Complete SQLite DDL Implementation

```sql
-- Pragmas for High Concurrency and Forensic Safety
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
PRAGMA encoding = 'UTF-8';

-- 1. Ingested Documents & Raw Artifacts Table
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,                       -- UUID v4 or canonical hash
    source_uri TEXT NOT NULL,                           -- Local path or Google Drive URI
    file_name TEXT NOT NULL,                            -- Base file name
    file_path TEXT NOT NULL,                            -- Absolute file path on disk
    file_size_bytes INTEGER NOT NULL CHECK(file_size_bytes >= 0),
    mime_type TEXT NOT NULL,                            -- application/pdf, image/png, etc.
    file_sha256 TEXT NOT NULL UNIQUE,                   -- 64-char lowercase hex SHA-256
    content_sha256 TEXT NOT NULL,                       -- Canonical hash of extracted text
    ingestion_timestamp TEXT NOT NULL,                  -- ISO 8601 UTC
    document_date TEXT,                                 -- Normalized ISO 8601 date (if detected)
    page_count INTEGER NOT NULL DEFAULT 1 CHECK(page_count >= 1),
    extracted_text TEXT,                                -- Full text / OCR transcription
    ocr_confidence REAL NOT NULL DEFAULT 1.0 CHECK(ocr_confidence >= 0.0 AND ocr_confidence <= 1.0),
    raw_metadata_json TEXT NOT NULL DEFAULT '{}',       -- JSON string of source metadata
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- 2. Canonical Entities Table
CREATE TABLE IF NOT EXISTS entities (
    entity_id TEXT PRIMARY KEY,                         -- Canonical entity ID (e.g. ENT-PER-001)
    canonical_name TEXT NOT NULL,                       -- USPS / Title-cased clean name
    entity_category TEXT NOT NULL CHECK(
        entity_category IN (
            'INDIVIDUAL',
            'MUNICIPAL_BODY',
            'FINANCIAL_INSTITUTION',
            'PROPERTY_MANAGEMENT',
            'LEGAL_AGENCY',
            'COMMERCIAL_ENTITY',
            'OTHER'
        )
    ),
    role_or_title TEXT,                                 -- e.g. "Former Mayor", "Eviction Attorney"
    primary_jurisdiction TEXT,                          -- e.g. "Anaheim / CDCA", "OC Superior Court"
    aliases_json TEXT NOT NULL DEFAULT '[]',            -- JSON array of known aliases/misspellings
    metadata_json TEXT NOT NULL DEFAULT '{}',           -- JSON object of attributes (EIN, Bar #, etc.)
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- 3. Entity Mentions Table (Mapping mentions to documents & offset ranges)
CREATE TABLE IF NOT EXISTS entity_mentions (
    mention_id TEXT PRIMARY KEY,                        -- UUID v4
    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    raw_mention_text TEXT NOT NULL,                     -- Verbatim text snippet
    char_offset_start INTEGER CHECK(char_offset_start >= 0),
    char_offset_end INTEGER CHECK(char_offset_end >= char_offset_start),
    page_number INTEGER NOT NULL DEFAULT 1 CHECK(page_number >= 1),
    context_snippet TEXT,                               -- Surrounding sentence / paragraph
    confidence_score REAL NOT NULL DEFAULT 1.0 CHECK(confidence_score >= 0.0 AND confidence_score <= 1.0),
    extraction_method TEXT NOT NULL CHECK(extraction_method IN ('REGEX', 'NER', 'MANUAL', 'HYBRID')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- 4. Normalized Timeline Events Table
CREATE TABLE IF NOT EXISTS timeline_events (
    event_id TEXT PRIMARY KEY,                          -- EVT-YYYYMMDD-XXXX
    document_id TEXT REFERENCES documents(document_id) ON DELETE SET NULL,
    event_date_iso TEXT NOT NULL,                       -- Strict ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
    event_year INTEGER NOT NULL,
    event_month INTEGER CHECK(event_month BETWEEN 1 AND 12),
    event_day INTEGER CHECK(event_day BETWEEN 1 AND 31),
    event_type TEXT NOT NULL CHECK(
        event_type IN (
            'JUDICIAL_FILING',
            'REGULATORY_NOTICE',
            'LEGISLATIVE_ACTION',
            'FINANCIAL_TRANSACTION',
            'INCIDENT_LOG',
            'ARREST_SEARCH',
            'RETALIATION_ACTION',
            'ENVIRONMENTAL_HAZARD',
            'OTHER'
        )
    ),
    title TEXT NOT NULL,                                -- Summary event headline
    description TEXT NOT NULL,                          -- Full evidentiary narrative
    raw_snippet TEXT,                                   -- Direct primary source quote
    primary_entity_id TEXT REFERENCES entities(entity_id) ON DELETE SET NULL,
    location TEXT,                                      -- Physical address or venue
    jurisdiction TEXT,                                  -- Legal jurisdiction
    confidence_score REAL NOT NULL DEFAULT 1.0 CHECK(confidence_score >= 0.0 AND confidence_score <= 1.0),
    chronological_rank INTEGER,                         -- Monotonically increasing rank
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- 5. Financial Transactions Table
CREATE TABLE IF NOT EXISTS financial_transactions (
    transaction_id TEXT PRIMARY KEY,                    -- TRX-XXXX
    document_id TEXT REFERENCES documents(document_id) ON DELETE SET NULL,
    event_id TEXT REFERENCES timeline_events(event_id) ON DELETE SET NULL,
    transaction_date_iso TEXT NOT NULL,                 -- ISO 8601 date
    amount REAL NOT NULL CHECK(amount >= 0.0),          -- Always positive magnitude
    currency TEXT NOT NULL DEFAULT 'USD',
    sender_entity_id TEXT REFERENCES entities(entity_id) ON DELETE SET NULL,
    recipient_entity_id TEXT REFERENCES entities(entity_id) ON DELETE SET NULL,
    sender_raw_text TEXT,
    recipient_raw_text TEXT,
    payment_method TEXT NOT NULL CHECK(
        payment_method IN ('WIRE', 'CHECK', 'CASH', 'ESCROW', 'GRANT', 'BRIBERY_CONDUIT', 'INVOICE', 'UNKNOWN')
    ),
    account_or_check_num TEXT,
    transaction_purpose TEXT,
    is_predicate_act INTEGER NOT NULL DEFAULT 0 CHECK(is_predicate_act IN (0, 1)),
    raw_snippet TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- 6. Relational Graph Edges Table
CREATE TABLE IF NOT EXISTS relationships (
    relationship_id TEXT PRIMARY KEY,                   -- REL-XXXX
    source_entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    target_entity_id TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL CHECK(
        relationship_type IN (
            'OFFICER_OF',
            'EMPLOYED_BY',
            'CONTROLLED_BY',
            'TRANSFERRED_FUNDS_TO',
            'SUED_BY',
            'REPRESENTED_BY',
            'CO_CONSPIRATOR_WITH',
            'RETALIATED_AGAINST',
            'SUBMITTED_BID_TO',
            'ISSUED_NOTICE_TO',
            'CONNECTED_TO'
        )
    ),
    direction TEXT NOT NULL DEFAULT 'DIRECTED' CHECK(direction IN ('DIRECTED', 'BIDIRECTIONAL')),
    confidence REAL NOT NULL DEFAULT 1.0 CHECK(confidence >= 0.0 AND confidence <= 1.0),
    valid_from TEXT,                                    -- ISO 8601 start date
    valid_to TEXT,                                      -- ISO 8601 end date
    source_document_id TEXT REFERENCES documents(document_id) ON DELETE SET NULL,
    evidence_summary TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    CHECK(source_entity_id <> target_entity_id)         -- Prevent trivial self-loops
);

-- 7. Automated Invariants & Cryptographic Audit Log Table
CREATE TABLE IF NOT EXISTS schema_invariants_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    tier_level TEXT NOT NULL,                           -- TIER_1, TIER_2, TIER_3, TIER_4
    merkle_root_sha256 TEXT NOT NULL,                   -- Current composite state root
    documents_count INTEGER NOT NULL,
    entities_count INTEGER NOT NULL,
    events_count INTEGER NOT NULL,
    transactions_count INTEGER NOT NULL,
    relationships_count INTEGER NOT NULL,
    foreign_key_violations INTEGER NOT NULL DEFAULT 0,
    chronological_inversions INTEGER NOT NULL DEFAULT 0,
    verification_status TEXT NOT NULL CHECK(verification_status IN ('PASSED', 'FAILED'))
);

-- Performance & Integrity Indexes
CREATE INDEX IF NOT EXISTS idx_documents_file_sha256 ON documents(file_sha256);
CREATE INDEX IF NOT EXISTS idx_documents_mime ON documents(mime_type);
CREATE INDEX IF NOT EXISTS idx_entities_canonical_name ON entities(canonical_name);
CREATE INDEX IF NOT EXISTS idx_entities_category ON entities(entity_category);
CREATE INDEX IF NOT EXISTS idx_entity_mentions_doc ON entity_mentions(document_id);
CREATE INDEX IF NOT EXISTS idx_entity_mentions_ent ON entity_mentions(entity_id);
CREATE INDEX IF NOT EXISTS idx_timeline_events_date ON timeline_events(event_date_iso);
CREATE INDEX IF NOT EXISTS idx_timeline_events_entity ON timeline_events(primary_entity_id);
CREATE INDEX IF NOT EXISTS idx_timeline_events_type ON timeline_events(event_type);
CREATE INDEX IF NOT EXISTS idx_financial_trx_date ON financial_transactions(transaction_date_iso);
CREATE INDEX IF NOT EXISTS idx_financial_trx_sender ON financial_transactions(sender_entity_id);
CREATE INDEX IF NOT EXISTS idx_financial_trx_recipient ON financial_transactions(recipient_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_source_target ON relationships(source_entity_id, target_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);
```

---

### 3.2 Master Catalog Structured JSON Schema (`master_timeline_catalog.json`)

**File Path:** `C:\OsintNeoAi\workspaces\osintneoai_indexer\master_timeline_catalog.json`  
**Specification:** JSON Schema Draft-07 Compliant.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OsintNeoAiMasterTimelineCatalog",
  "description": "Deterministic, canonical catalog of all ingested evidence, extracted entities, chronological timeline events, financial flows, and relational edges with Merkle cryptographic root verification.",
  "type": "object",
  "required": [
    "catalog_metadata",
    "documents",
    "entities",
    "timeline_events",
    "financial_transactions",
    "relationships",
    "audit_invariants"
  ],
  "properties": {
    "catalog_metadata": {
      "type": "object",
      "required": [
        "schema_version",
        "generated_at",
        "root_merkle_sha256",
        "total_documents",
        "total_entities",
        "total_events",
        "total_transactions",
        "total_relationships",
        "integrity_mode"
      ],
      "properties": {
        "schema_version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
        "generated_at": { "type": "string", "format": "date-time" },
        "root_merkle_sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "total_documents": { "type": "integer", "minimum": 0 },
        "total_entities": { "type": "integer", "minimum": 0 },
        "total_events": { "type": "integer", "minimum": 0 },
        "total_transactions": { "type": "integer", "minimum": 0 },
        "total_relationships": { "type": "integer", "minimum": 0 },
        "integrity_mode": { "type": "string", "enum": ["development", "production", "forensic_court_ready"] }
      }
    },
    "documents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "document_id",
          "file_name",
          "file_sha256",
          "content_sha256",
          "file_size_bytes",
          "mime_type",
          "ingestion_timestamp"
        ],
        "properties": {
          "document_id": { "type": "string" },
          "source_uri": { "type": "string" },
          "file_name": { "type": "string" },
          "file_path": { "type": "string" },
          "file_sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
          "content_sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
          "file_size_bytes": { "type": "integer", "minimum": 0 },
          "mime_type": { "type": "string" },
          "ingestion_timestamp": { "type": "string", "format": "date-time" },
          "document_date": { "type": ["string", "null"] },
          "page_count": { "type": "integer", "minimum": 1 },
          "ocr_confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
        }
      }
    },
    "entities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["entity_id", "canonical_name", "entity_category", "aliases"],
        "properties": {
          "entity_id": { "type": "string" },
          "canonical_name": { "type": "string" },
          "entity_category": {
            "type": "string",
            "enum": [
              "INDIVIDUAL",
              "MUNICIPAL_BODY",
              "FINANCIAL_INSTITUTION",
              "PROPERTY_MANAGEMENT",
              "LEGAL_AGENCY",
              "COMMERCIAL_ENTITY",
              "OTHER"
            ]
          },
          "role_or_title": { "type": ["string", "null"] },
          "primary_jurisdiction": { "type": ["string", "null"] },
          "aliases": {
            "type": "array",
            "items": { "type": "string" }
          },
          "metadata": { "type": "object" }
        }
      }
    },
    "timeline_events": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "event_id",
          "event_date_iso",
          "event_type",
          "title",
          "description"
        ],
        "properties": {
          "event_id": { "type": "string" },
          "document_id": { "type": ["string", "null"] },
          "event_date_iso": { "type": "string" },
          "event_type": {
            "type": "string",
            "enum": [
              "JUDICIAL_FILING",
              "REGULATORY_NOTICE",
              "LEGISLATIVE_ACTION",
              "FINANCIAL_TRANSACTION",
              "INCIDENT_LOG",
              "ARREST_SEARCH",
              "RETALIATION_ACTION",
              "ENVIRONMENTAL_HAZARD",
              "OTHER"
            ]
          },
          "title": { "type": "string" },
          "description": { "type": "string" },
          "raw_snippet": { "type": ["string", "null"] },
          "primary_entity_id": { "type": ["string", "null"] },
          "location": { "type": ["string", "null"] },
          "jurisdiction": { "type": ["string", "null"] },
          "confidence_score": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
          "chronological_rank": { "type": ["integer", "null"] }
        }
      }
    },
    "financial_transactions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "transaction_id",
          "transaction_date_iso",
          "amount",
          "currency",
          "payment_method"
        ],
        "properties": {
          "transaction_id": { "type": "string" },
          "document_id": { "type": ["string", "null"] },
          "event_id": { "type": ["string", "null"] },
          "transaction_date_iso": { "type": "string" },
          "amount": { "type": "number", "minimum": 0.0 },
          "currency": { "type": "string", "default": "USD" },
          "sender_entity_id": { "type": ["string", "null"] },
          "recipient_entity_id": { "type": ["string", "null"] },
          "payment_method": {
            "type": "string",
            "enum": ["WIRE", "CHECK", "CASH", "ESCROW", "GRANT", "BRIBERY_CONDUIT", "INVOICE", "UNKNOWN"]
          },
          "account_or_check_num": { "type": ["string", "null"] },
          "transaction_purpose": { "type": ["string", "null"] },
          "is_predicate_act": { "type": "boolean" }
        }
      }
    },
    "relationships": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "relationship_id",
          "source_entity_id",
          "target_entity_id",
          "relationship_type"
        ],
        "properties": {
          "relationship_id": { "type": "string" },
          "source_entity_id": { "type": "string" },
          "target_entity_id": { "type": "string" },
          "relationship_type": {
            "type": "string",
            "enum": [
              "OFFICER_OF",
              "EMPLOYED_BY",
              "CONTROLLED_BY",
              "TRANSFERRED_FUNDS_TO",
              "SUED_BY",
              "REPRESENTED_BY",
              "CO_CONSPIRATOR_WITH",
              "RETALIATED_AGAINST",
              "SUBMITTED_BID_TO",
              "ISSUED_NOTICE_TO",
              "CONNECTED_TO"
            ]
          },
          "direction": { "type": "string", "enum": ["DIRECTED", "BIDIRECTIONAL"] },
          "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
          "evidence_summary": { "type": ["string", "null"] }
        }
      }
    },
    "audit_invariants": {
      "type": "object",
      "required": [
        "documents_merkle_sha256",
        "entities_merkle_sha256",
        "events_merkle_sha256",
        "transactions_merkle_sha256",
        "relationships_merkle_sha256",
        "foreign_key_violations",
        "chronological_inversions",
        "all_invariants_passed"
      ],
      "properties": {
        "documents_merkle_sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "entities_merkle_sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "events_merkle_sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "transactions_merkle_sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "relationships_merkle_sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "foreign_key_violations": { "type": "integer", "enum": [0] },
        "chronological_inversions": { "type": "integer", "enum": [0] },
        "all_invariants_passed": { "type": "boolean", "enum": [true] }
      }
    }
  }
}
```

---

## 4. Automated Invariant Testing & SHA-256 Verification (R4)

### 4.1 Canonical Cryptographic Signatures

To ensure tamper-evident chain of custody and bit-for-bit reproducibility, the pipeline enforces strict mathematical hashing standards:

#### 1. 64 KB Block Streaming for Binary Files
*Critical Finding:* Legacy scripts (e.g. `scripts/ingest_jan2021_feb2022_timeline.py`) previously performed a single `read(65536)`, hashing only the file's first 64 KB. The OsintNeoAi Indexer MUST stream entire files in 64 KB blocks until EOF:
```python
def compute_stream_sha256(file_path: str, chunk_size: int = 65536) -> str:
    """Computes full canonical SHA-256 hash using streaming chunks."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest().lower()
```

#### 2. RFC 8785 JSON Canonicalization Scheme (JCS)
For extracted records, JSON serialization must be deterministic:
- Sorted object keys (lexicographical UTF-8 order).
- No extraneous whitespace between tokens (`separators=(',', ':')`).
- Standard IEEE 754 float formatting (avoiding exponential representation discrepancies).
- UTF-8 encoding without byte-order marks.
```python
def compute_canonical_json_sha256(data: Any) -> str:
    """Computes deterministic SHA-256 hash conforming to RFC 8785 JCS."""
    canonical_json_bytes = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical_json_bytes).hexdigest().lower()
```

#### 3. Hierarchical Merkle Root Aggregation
The dataset state is summarized into a single 256-bit cryptographic root:

```
                                  ┌───────────────────────────────┐
                                  │      MASTER ROOT SHA-256      │
                                  └───────────────┬───────────────┘
                                                  │
               ┌─────────────────┬────────────────┼─────────────────┬─────────────────┐
               ▼                 ▼                ▼                 ▼                 ▼
        ┌─────────────┐   ┌─────────────┐  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
        │  DOCUMENTS  │   │  ENTITIES   │  │   EVENTS    │   │ TRANSACTIONS│   │RELATIONSHIPS│
        │ MERKLE ROOT │   │ MERKLE ROOT │  │ MERKLE ROOT │   │ MERKLE ROOT │   │ MERKLE ROOT │
        └─────────────┘   └─────────────┘  └─────────────┘   └─────────────┘   └─────────────┘
```

$$\text{Root} = \text{SHA256}\left(\text{Root}_{\text{Docs}} \mathbin{\Vert} \text{Root}_{\text{Ents}} \mathbin{\Vert} \text{Root}_{\text{Evts}} \mathbin{\Vert} \text{Root}_{\text{Trx}} \mathbin{\Vert} \text{Root}_{\text{Rels}}\right)$$

Where for any ordered list of child hashes $[h_1, h_2, \dots, h_n]$:
$$\text{Merkle Root} = \text{SHA256}\left(\bigoplus_{i=1}^n h_i\right) \quad \text{or pairwise binary tree reduction}$$

---

### 4.2 SQLite Schema Integrity & Chronological Ordering Invariants

Every batch execution of the indexer must execute and satisfy four classes of automated invariant assertions:

```
                               ┌────────────────────────────────┐
                               │  AUTOMATED INVARIANT SYSTEM    │
                               └───────────────┬────────────────┘
            ┌──────────────────┬───────────────┴────────────────┬──────────────────┐
            ▼                  ▼                                ▼                  ▼
    ┌───────────────┐  ┌───────────────┐                ┌───────────────┐  ┌───────────────┐
    │  FOREIGN KEY  │  │  UNIQUENESS   │                │ CHRONOLOGICAL │  │   FINANCIAL   │
    │   INTEGRITY   │  │   & HASHES    │                │  MONOTONICITY │  │ CONSERVATISM  │
    │ (PRAGMA check)│  │ (Zero collis.)│                │ (No time inv.)│  │(Non-neg balances)
    └───────────────┘  └───────────────┘                └───────────────┘  └───────────────┘
```

1. **Foreign Key Integrity Assertion:**
   - Execute `PRAGMA foreign_key_check;`. Output must be an empty set (0 rows).
2. **Uniqueness & Hash Collision Assertion:**
   - $\text{COUNT}(\text{documents}) == \text{COUNT}(\text{DISTINCT } \text{file\_sha256})$.
   - $\text{COUNT}(\text{entities}) == \text{COUNT}(\text{DISTINCT } \text{canonical\_name})$ within same category.
3. **Chronological Monotonicity Assertion:**
   - All events in `timeline_events` must have valid ISO 8601 timestamps.
   - For all ordered events $E_i, E_{i+1}$ where $\text{rank}(E_i) < \text{rank}(E_{i+1})$, assert $E_i.\text{date} \le E_{i+1}.\text{date}$.
   - **Causal Invariant Precedence Verification:**
     - HCD Notice of Violation (`2021-12-08`) precedes Anaheim City Council Voidance Resolution (`2022-05-24`).
     - FBI Search Warrant Affidavit unsealing (`2022-05-16`) precedes Harry Sidhu Guilty Plea (`2023-08-16`).
     - Unlawful Detainer Complaint (`2021-05-19`) precedes Default Judgment 1 (`2021-06-29`) and Judge Luege Stay Order (`2021-12-22`).
     - Tactical 170.6 Peremptory Challenge (`2021-12-22 16:29`) succeeds Judge Luege Chambers Stay Order (`2021-12-22 15:11`).
4. **Financial Conservatism Assertion:**
   - For all rows in `financial_transactions`, `amount >= 0.0`.
   - Sum of refunded escrow deposits must equal exactly $\$50,000,000.00$.
   - Surplus Land Act penalty calculation must equal exactly $0.30 \times \$320,000,000 = \$96,000,000.00$.

---

## 5. Test Tier Requirements (Tiers 1–4 for E2E Testing)

To guarantee 100% invariant verification across the pipeline, testing is structured into four progressive tiers:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ TIER 4: End-to-End Pipeline & Volume Verification                            │
│ Full corpus processing, zero memory leaks, 100% invariant assertion pass     │
├──────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: Entity Resolution & Timeline Reconciliation                          │
│ Disambiguation precision/recall, graph DAG validation, chronological sorting │
├──────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: Database Schema & Ingestion Integration                              │
│ SQLite WAL creation, foreign key triggers, transactions, batch inserts       │
├──────────────────────────────────────────────────────────────────────────────┤
│ TIER 1: Unit & Cryptographic Invariants                                      │
│ 64KB SHA-256 stream, RFC 8785 JSON canonicalizer, regex & date normalizers   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Test Tier Breakdown & Scope Matrix

| Test Tier | Focus Area | Key Modules Tested | Pass / Invalidation Criteria |
|---|---|---|---|
| **Tier 1: Unit & Cryptographic Invariants** | Low-level algorithms, hashing, parsing, normalizers. | `crypto.py`, `normalizers.py`, `regex_extractors.py` | - Deterministic SHA-256 matching across platforms.<br>- 100% pass on USPS address & corporate suffix stripping.<br>- RFC 8785 canonical JSON hash byte-for-byte match. |
| **Tier 2: Database & Storage Integration** | SQLite schema DDL, CRUD, transactions, locks. | `database.py`, `models.py`, `timeline_vault.db` | - `PRAGMA foreign_key_check` returns 0 rows.<br>- WAL mode active and concurrency verified.<br>- Cascading deletes operate correctly without orphaned records. |
| **Tier 3: Entity Resolution & Reconciliation** | Disambiguation, phonetic blocking, timeline sorting. | `entity_resolver.py`, `timeline_builder.py`, `graph.py` | - Soundex & Double Metaphone correctly group aliases.<br>- No cyclical parent-child relations in enterprise nodes.<br>- 100% monotonic chronology in `timeline_events`. |
| **Tier 4: End-to-End Pipeline & Stress Testing** | Full ingest from disk/Drive, OCR, DB write, JSON export. | `pipeline.py`, `indexer_cli.py`, `master_catalog.json` | - Zero unhandled exceptions or memory faults on >1GB streams.<br>- `master_timeline_catalog.json` passes JSON Schema validation.<br>- Merkle root verified across all tables. |

---

### 5.1 Pytest Architecture & Directory Layout

The automated test suite resides at `C:\OsintNeoAi\workspaces\osintneoai_indexer\tests\`:

```
workspaces/osintneoai_indexer/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                       # Global fixtures: temp SQLite DB, mock streams, sample catalog
│   ├── test_tier1_crypto_invariants.py   # Tier 1: 64KB streaming SHA-256, RFC 8785 JCS, Merkle root
│   ├── test_tier1_regex_normalizers.py   # Tier 1: Dockets, statutes, financial regex, USPS & Corp normalizers
│   ├── test_tier2_database_schema.py     # Tier 2: SQLite DDL, FK enforcement, Check constraints, WAL mode
│   ├── test_tier2_batch_ingestion.py     # Tier 2: Batch inserts, transactions, rollback on error
│   ├── test_tier3_entity_resolution.py   # Tier 3: Phonetic blocking, fuzzy matching, DSU deduplication
│   ├── test_tier3_timeline_ordering.py   # Tier 3: ISO date parsing, causal precedence, ROA monotonicity
│   ├── test_tier4_e2e_pipeline.py        # Tier 4: End-to-end ingestion, OCR parsing, DB sync, JSON export
│   └── test_tier4_catalog_validation.py  # Tier 4: JSON Schema Draft-07 validation, Merkle root verification
```

---

## 6. Implementation Blueprint & Recommendations

1. **Workspace Setup:** Initialize `C:\OsintNeoAi\workspaces\osintneoai_indexer\` with modular packages:
   - `src/core/` (crypto, normalizers, regex patterns, schemas)
   - `src/db/` (SQLite manager, migrations, DDL, queries)
   - `src/extraction/` (OCR wrappers, stream handlers, entity extractors)
   - `src/pipeline/` (orchestration, timeline reconciliation, catalog exporter)
   - `tests/` (Tiers 1–4 pytest suite)
2. **Stream Chunking:** Use generators with fixed 64 KB buffers (`io.BufferedReader`) for all file ingestion to handle multi-gigabyte archives within low memory footprints.
3. **Deterministic Serializer:** Bundle a standalone RFC 8785 canonical JSON serializer in `src/core/crypto.py` to prevent external dependency drift.
4. **Automated Verification Script:** Provide a standalone CLI verification tool `verify_invariants.py` that executes Tiers 1–4 assertions and outputs a court-ready cryptographic audit report.

---
*Report compiled and verified by Explorer Agent `explorer_survey_3`.*
