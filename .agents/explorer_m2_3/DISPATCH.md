## 2026-08-29T17:51:17Z
You are Explorer 3 for Milestone 2 (M2: Deep Text Extraction & OCR Engine) of the OsintNeoAi Indexer project.
Your Working Directory: C:\OsintNeoAi\.agents\explorer_m2_3\

Authoritative Context:
- Project Plan: C:\OsintNeoAi\PROJECT.md (M2 Scope, Features 8-11, Interface Contracts)
- User Request: C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md (## 2026-08-29T17:34:35Z)
- User Rules & Backups: C:\OsintNeoAi\AGENTS.md
- Prior Survey Analysis: C:\OsintNeoAi\.agents\explorer_survey_2\analysis.md and C:\OsintNeoAi\.agents\explorer_survey_3\analysis.md

Your Task:
Investigate and design the exact technical specification, module interfaces, regex algorithms, and implementation blueprints for:
1. `C:\OsintNeoAi\workspaces\osintneoai_indexer\normalizers\date_normalizer.py`:
   - ISO 8601 UTC date parser handling 15+ date formats (legal filing stamps, court docket entries, email RFC 2822, fuzzy English dates e.g. "December 8, 2021", "2021 JUN 29 PM 4:29").
2. `C:\OsintNeoAi\workspaces\osintneoai_indexer\normalizers\financial_normalizer.py`:
   - Dual representation parser ($ float and integer cents) handling $320M, $96 Million, $1.5M, $250k, negative parenthetical amounts `($500.00)`, comma-separated values, and currency symbols.
3. `C:\OsintNeoAi\workspaces\osintneoai_indexer\normalizers\case_normalizer.py`:
   - Legal docket and statutory citation extractor (USDC CDCA/DNJ federal cases e.g. `8:23-cr-00108-CJC`, California Superior Court e.g. `30-2021-01201327-CL-UD-CJC`, Cal. Gov. Code § 54220, Cal. CCP § 170.6).
4. `C:\OsintNeoAi\workspaces\osintneoai_indexer\normalizers\entity_normalizer.py`:
   - Corporate legal suffix normalizer, Russell Soundex, and Double Metaphone phonetic encoders.

Deliverables:
- Write detailed implementation plan and code specifications to `C:\OsintNeoAi\.agents\explorer_m2_3\analysis.md`
- Write 5-component handoff report to `C:\OsintNeoAi\.agents\explorer_m2_3\handoff.md`
- Send completion message to parent orchestrator.
