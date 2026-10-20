## 2026-08-29T17:56:14Z
You are the Implementation Worker for Milestone 2 (M2: Deep Text Extraction & OCR Engine) of the OsintNeoAi Indexer project.
Your Working Directory: C:\OsintNeoAi\.agents\worker_m2\
Target Workspace: C:\OsintNeoAi\workspaces\osintneoai_indexer\

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Read authoritative files first:
1. C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md (specifically ## 2026-08-29T17:34:35Z)
2. C:\OsintNeoAi\PROJECT.md (M2 Scope, Features 5-11, Interface Contracts)
3. C:\OsintNeoAi\AGENTS.md
4. Explorer blueprints:
   - C:\OsintNeoAi\.agents\explorer_m2_1\analysis.md (OCR engine, image enhancer, document extractor fallback ladder)
   - C:\OsintNeoAi\.agents\explorer_m2_2\analysis.md (Format extractors: TIFF, HTML, DOCX, Images, Text/CSV/JSON)
   - C:\OsintNeoAi\.agents\explorer_m2_3\analysis.md (Normalizers: Date, Financial, Case dockets, Entity normalizers)

Files You Exclusively Own & Must Implement:
- C:\OsintNeoAi\workspaces\osintneoai_indexer\extractors\__init__.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\extractors\ocr_engine.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\extractors\image_enhancer.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\extractors\format_extractors.py (or modular tiff, html, docx, image, text extractors)
- C:\OsintNeoAi\workspaces\osintneoai_indexer\extractors\document_extractor.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\normalizers\__init__.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\normalizers\date_normalizer.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\normalizers\financial_normalizer.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\normalizers\case_normalizer.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\normalizers\entity_normalizer.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\tests\test_m2_extraction.py

Requirements & Acceptance Criteria:
1. Implement the 5-Tier Fallback Ladder (PyMuPDF native text -> density check -> 300 DPI pixmap rendering -> RapidOCR ONNX -> OpenCV CLAHE enhancement -> Format parsers).
2. Guarantee $O(1)$ memory usage (< 250 MB RAM cap) with explicit generator streaming and pixmap memory release (`del pix; del img_np; gc.collect()`).
3. Implement all normalizers:
   - ISO 8601 UTC date parsing across 15+ formats.
   - Financial parser with exact integer cents and floating-point values using `Decimal` arithmetic.
   - Federal and California Superior Court docket numbers and statutory citations.
   - Corporate legal suffix cleaning, Russell Soundex, and Double Metaphone phonetic encoding.
4. Implement comprehensive unit tests in `tests/test_m2_extraction.py` covering all extractors and normalizers. Run `pytest` and verify 100% passing tests.
5. Write a comprehensive 5-component handoff report to `C:\OsintNeoAi\.agents\worker_m2\handoff.md` with complete test output, and send a completion message to the parent orchestrator (34f685b0-e5c3-4fa3-aac5-dc635a0add4e).
