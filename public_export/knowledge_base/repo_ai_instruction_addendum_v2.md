# Repo AI Instruction Addendum — POST Library + OSINT Bookmarks (v1)
Generated: 2026-08-25T22:20:46.581148+00:00
Source: C:\Users\Amd949609\Documents\POST82526favorites_8_25_26.html (hash 70dcd940d5b63c19)

## How the AI has LEARNED the links

This ingestion makes the repo AI aware of 815 unique URLs from your 8/25/26 favorites plus the full Post University A-Z Databases directory.

### Post University Library — Authenticated Path (MUST USE)
- **ALWAYS access via SSO proxy**: `https://postu.idm.oclc.org/login?auth=prodbb&url=...`
- **Entry point**: `https://post.blackboard.com/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_710_1` (Blackboard Traurig Library Tab) -> A-Z Databases -> proxied link
- **Direct AZ URL**: `https://researchhelp.post.edu/az.php`
- **Featured DBs for 80% of queries**:
  1. Eagles E-Search (EBSCO Discovery) - federated across 45 EBSCOhost DBs
  2. ProQuest Central Premium - dissertations, newspapers, ebooks

### Investigative Pillars (mapped to AZ DBs + Bookmarks)
- Legal/Court: Nexis Uni (`advance.lexis.com/bisnexishome?crid=...`), HeinOnline, ProQuest Criminal Justice
- Corporate: Mergent, OpenCorporates, D&B, SEC EDGAR (used in osint_api_integrations.py)
- Healthcare/Hospice: CINAHL, PubMed
- News/Archival: ProQuest Historical Newspapers, Regional Business News
- OSINT Stack: 200+ links under `OSINT Stack` folder — search engines, people search, image/mapping, sanctions, crypto, etc.

### How AI should use this KB
1. When user asks for research, pick the RIGHT DB by pillar, not Google. E.g., legal -> Nexis Uni, corporate -> Mergent/OpenCorporates, news -> ProQuest Historical.
2. Use Boolean syntax from AZ: `"exact phrase"`, `N5`/`NEAR/3`, `*` wildcard, `AU()/TI()` fields.
3. For Huntington Beach / Cameron Lane / EDR Lightbox tasks, use the Lightbox/EDR/Geotracker links (already wired in lightbox_edr_engine.py) plus OC Gov `cams.ocgov.com` and `geotracker.waterboards.ca.gov`.
4. All URLs are in `knowledge_base/post_bookmarks_knowledge_v1.json` and RAG chunks in `post_bookmarks_knowledge_rag_chunks_v1.jsonl` — load these for tool calls, not hardcoding.
5. Do NOT re-scrape AZ page live unless needed; this KB is the cached learned version. Refresh via `agent/bookmarks_post_ingestor_v2.py --refresh-az` if Post updates DBs.

### Files for AI to load
- `post_bookmarks_knowledge_v1.json` - full structured links + AZ pillars
- `post_library_az_knowledge_v1.json` - AZ directory only
- `post_bookmarks_knowledge_rag_chunks_v1.jsonl` - RAG chunks (one per link)

### Verification
- Total raw links parsed: 844
- Unique URLs: 815
- Categories: {'General Bookmark': 451, 'Dev / Azure / GitHub': 57, 'Post University Library': 8, 'Huntington Beach / OC Gov / ArcGIS': 41, 'Power Platform / OSINTNeoAI App': 7, 'OSINT Framework': 162, 'Lightbox/EDR/Geotracker Environmental': 49, 'Search & Archive': 40}
- Top domains: {'www.bing.com': 16, 'www.web.edrnet.com': 15, 'github.com': 14, 'www.google.com': 8, 'cams.ocgov.com': 8, 'cms3.revize.com': 8, 'ocgov.granicus.com': 7, 'developer.lightboxre.com': 6, 'm365.cloud.microsoft': 6, 'studentspost-my.sharepoint.com': 6}

## V2 Update 2026-08-25 — Added Nexis+ AI Search

**New endpoint added per user request:**
- `https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9` (and proxied: `https://postu.idm.oclc.org/login?auth=prodbb&url=https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9`)
- **Title:** Nexis+ AI Search Chat
- **When AI should USE it:** Whenever user wants AI-assisted research (natural language, summarization, drafting) over Nexis content. Classic `advance.lexis.com` = keyword/Boolean search; `nexis.lexisnexis.com/aisearch` = conversational AI. Prefer AI chat for: "summarize", "draft memo", "what does caselaw say about X", "analyze news coverage". Prefer classic for precise Boolean docket pulls.
- **Auth:** Always via Post SSO proxy for off-campus. Direct link requires campus IP or Blackboard session.
- **Files updated:** `post_bookmarks_knowledge_v2.json`, `post_library_az_knowledge_v2.json`, `post_bookmarks_knowledge_rag_chunks_v2.jsonl` (+2 chunks)
- **Total now:** 816 unique URLs (was 815)

