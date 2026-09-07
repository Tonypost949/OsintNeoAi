# Final System Architecture Breakdown: OsintNeoAi & TaxFunded.app

**CORE PLATFORM PHILOSOPHY (The "Single Engine / One Brain" Doctrine):**
*   **One Brain, Different Expressions:** It is one central intelligence layer with different inputs and a few ways to express itself as outputs.
*   **Unique Receptors, Same Nerves:** Some inputs (like the Chrome Extension vs. the public 'Who Hurt You' Chat AI) have unique receptors tailored to the user, but they share the exact same underlying nerves. They route data through the exact same core pipeline and validation engine.
*   **The Data Lifecycle (Virtual Pointers, No Physical Duplication):**
    1. Everything of value is **Data**.
    2. All Data is given its own page/block on the base **OSINT Ledger**.
    3. The Data is enriched with **Attributes** strictly by the System Engine, not the User.
    4. Attributes are coded as **Meta** (Title, Description, Tags). Users cannot manually overwrite or define this metadata; it is a system-controlled, deterministic process.
        * *Human-in-the-Loop Contestation:* If the System extracts incorrect meta (e.g., AI hallucination), the user can leave a **Comment / Flag**. This does *not* overwrite the data. Instead, it generates a "Review Task" in the Task Ledger. If the review confirms the AI was wrong, the *System* appends a corrected version of the meta.
    5. Some Meta is standard (Title, Description) and stays purely on the OSINT Ledger. Other Meta triggers unique ledgers (e.g., `[TaxFunded]`, `[Task]`).
    6. If Data triggers another ledger, it is **virtually duplicated via pointers, but never physically duplicated.** 
    *CRITICAL REFINEMENT (Append-Only):* Because the System (not the user) defines the meta, the risk of user-tampering is eliminated. However, if the System updates the meta later (e.g., finding new entities, or correcting a user-flagged error), it uses an Append-Only (Event Sourced) model to preserve the original evidentiary hash version.
*   **Shared Software, Interconnected Newspapers:** The exact same UI rendering software builds the newspapers, but they query different datasets and interlink where investigations overlap.
*   **Shared Backend, Meta-Defined Ledgers:** There is only **one** backend software engine and toolset. The separation exists entirely at the data layer. Ledgers are meta-defined, and data attributes dynamically grow or shrink based on unique factors (e.g., TaxFunded tagging, FOIA requirements, etc.).

## 1. Identity & Constraints

---

## 2. THE TWIN PLATFORMS (Separation of Concerns)

The ecosystem is split into two distinct, 100% online platforms:

### A. OsintNeoAi (The Engine & Workspace)
This is the active builder and investigator environment.
*   **Purpose:** Multi-user workspaces, tool execution, API processing, and evidence ingestion.
*   **Access:** Users log in (using their crypto wallet) to access their personal workspace.
*   **Capabilities:** Users run OSINT tools, submit evidence anonymously, manage their investigations, and interact with the BigQuery graph databases.

### B. TaxFunded (The Presentation & Public Record)
This is the public-facing newspaper broadsheet.
*   **Purpose:** Public transparency, reading verified findings, and viewing the ledgers.
*   **Access:** Highly secure, **100% READ-ONLY** to the public. 
*   **The Single Exception:** The *only* interactive component on TaxFunded is a single **AI Chat Interface**.
*   **AI Chat Modes:** 
    1. *Wide Open:* General AI capabilities.
    2. *Grounded:* Strict RAG (Retrieval-Augmented Generation) locked exclusively to the verified evidence and ledger data published on the site.

---

## 2. THE TWO SEPARATE BLOCKCHAIN LEDGERS

### Phase 2: Omnichannel Evidence Ingestion
**Rule:** The core backend ingestion pipe is singular and isolated. The user-facing tools are merely "Input Scopes" that format data and throw it over the wall to the unified backend.

*   **Input Scope 1: The AI Chat:** The conversational UI is just an input point. If a user drops a link in the chat, the chat doesn't process it—it forwards it to the Ingestion Pipe.
*   **Input Scope 2: The Chrome Extension (`tab-copy`):** Configured for the `Ctrl+Shift+X` single-window scope, formatting multi-tab data into JSON and hitting the pipeline.
*   **Input Scope 3: Manual Dashboard Input:** For edge cases or mobile users.
*   **The Core Ingestion Engine (`workspace_api.py`):** Receives the payload from *any* scope and triggers the **Waterfall Tool Executor**.
*   **Living Legal Framework (Statutory Extraction & Indexing):** 
    *   **Data Schema:** The public legal section is a highly sortable, searchable column-row table. It extracts and displays *only*: Title, Code, Year, Type of Law, Jurisdiction (open text), Specific Jurisdiction Type (multi-choice: County/City/State/Fed), Government Type (e.g., Charter City, Commonwealth), TaxFunded Flag ('TaxFunded' or blank), 1-Sentence Description, Frequency Count, and an Official Hyperlink Button.
    *   **Native Search & Highlight:** The UI includes a native keyword search bar. Any matching keywords are dynamically highlighted across the table, with up/down arrow buttons to automatically jump/scroll to the next instance (bypassing the need for browser Ctrl+F).
    *   **No-Hosting Rule:** The platform acts strictly as an index and router. It does *not* host the full definitions or text of the laws.
    *   **Defect Section ("Someone Ain't Doing Their Job"):** If a law is cited but the official government link is missing or broken, it is dumped into a special section at the bottom of the page. An automated admin alert is triggered to investigate why the public record is inaccessible.
    *   **Visibility:** The public sees the global aggregated list. Individual users have a private version scoped to their 3 investigations. The "Featured User" (NWORICO) has their specific legal section exposed publicly via the Featured Story link.

Every piece of data across both sites is represented as an immutable asset on a blockchain ledger. Because data purity is critical, there are **two strictly separated ledgers**:

### Ledger 1: TaxFunded Ledger (Crypto: TFT)
*   **Scope & Coverage:** Strictly limited to **Federal Grants** (nationwide) and **California Grants** (state/local).
*   **The Front Page (Read-Only Matrix):** The primary view is a read-only newspaper/dashboard tracking exactly who is getting the money, historical recipients, and the exact dollar amounts.
*   **Entity Graphing:** The ingestion engine must extract and map the entire organizational graph for any grant recipient: NGOs, Corporate Officers, Registered Addresses, and Private Parent Companies that own the NGOs.
*   **Zero-Cost Data Mandate:** Because this is public taxpayer money, the platform must rely on free, open public data sources (e.g., USASpending.gov, CA Grants Portal, ProPublica Nonprofit Explorer, IRS 990 Bulk Data, Data.gov / Data.org) to populate the TaxFunded site, incurring zero paywall or premium API costs for the data gathering.
*   **Mandatory Entity-Hosted Data:** Every entity tracked on the TaxFunded ledger (from government agencies down to the NGOs receiving the money) has transparency mandates. The ingestion engine actively scrapes the official domains of these entities for their required self-hosted disclosures. Failure to host required data is flagged as an anomaly.
*   **Isolated Task System:** TaxFunded uses the exact same mechanical Task System UI and queue logic as OsintNeoAi, but operates on its own dedicated task ledger. The OSINT tasks and TaxFunded tasks are strictly separated to maintain focus on financial/grant audits.
*   **TaxFunded Legal UI Override:** The Legal Section on the TaxFunded site uses the exact same dynamic indexing system as OsintNeoAi, but leverages the `TaxFunded` column flag to render a dedicated, highly visible section at the very top of the page exclusively for taxpayer-funded laws and grant compliance codes.
*   **Shared Architecture:** While it operates as its own website and newspaper, fundamentally it uses the exact same underlying OSINT database, just filtered by `[Tax-Funded]` tags with extended financial/legal attributes.
*   **Reward:** Because these assets carry a higher burden of public responsibility, they trigger **Dual Rewards**. The submitter receives **TFT** *and* **OSINT** (since all taxpayer data is technically also OSINT data). The asset is recorded on both ledgers.

### Ledger 2: OSINT Ledger (Crypto: OSINT)
*   **Strict Rule:** For general intelligence that does *not* involve taxpayer money.
*   **Asset Types:** Purely private corporate fraud, private environmental hazards (Lightbox EDRs), private LLC tracking.
*   **Reward:** Users receive **OSINT (OsintCoin)** only. The asset is recorded only on the OSINT ledger.

*(Note: The `DualAuditTokenBridge` connects these two ledgers strictly for rewarding the user's unified wallet, but the data assets themselves never cross chains).*

---

## 3. UNIFIED IDENTITY, WORKSPACES & DATA CROSSING

*   **One Identity:** `User ID` = `Wallet Address` = `Workspace ID` = `Author Identity`.
*   Everything a user does is tied to their wallet, but their real-world identity remains completely anonymous.
*   **Investigation Limits:** A user's workspace can hold a maximum of **3 Active Investigations** at any time.
*   **Internal Data Crossing:** Data assets can be shared across a user's own 3 investigations. If a piece of evidence is used in multiple, the asset UI explicitly tags it as being utilized in multiple active investigations.
*   **User-to-User Crossing:** Currently disabled. User workspaces are isolated from each other for security and privacy.
*   **The Creator Scrub (NWORICO Intersection):**
    *   The system runs an automated daily BigQuery graph scrub across *all* user data.
    *   If any user's evidence connects or matches evidence inside the Creator's Featured Investigation (`NWORICO`), the system flags it.
    *   The user receives an alert: *"You have found data that fits the Creator's investigation."* This encourages a unified decentralized intelligence gathering effort toward the platform's primary targets.

---

## 4. EVASIVE OSINT SUBMISSION ENGINE

*   Users do not execute scans directly on their own devices.
*   Submissions pass through a decoupled middleware proxy.
*   **Metadata Stripping:** All IP addresses, User-Agent strings, device headers, and EXIF data (from images/PDFs) are aggressively stripped before the data hits the ledger or the OSINT tools.
*   **Attribution:** Users receive a cryptographic SHA-256 receipt proving they submitted the data (for token rewards) without exposing who they are.
