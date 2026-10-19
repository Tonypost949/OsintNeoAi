## 2026-08-29T17:51:17Z
You are Explorer 1 for Milestone 2 (M2: Deep Text Extraction & OCR Engine) of the OsintNeoAi Indexer project.
Your Working Directory: C:\OsintNeoAi\.agents\explorer_m2_1\

Authoritative Context:
- Project Plan: C:\OsintNeoAi\PROJECT.md (M2 Scope, Features 5-7, Interface Contracts)
- User Request: C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md (## 2026-08-29T17:34:35Z)
- User Rules & Backups: C:\OsintNeoAi\AGENTS.md
- Prior Survey Analysis: C:\OsintNeoAi\.agents\explorer_survey_2\analysis.md
- Milestone 1 Deliverables: C:\OsintNeoAi\workspaces\osintneoai_indexer\

Your Task:
Investigate and design the exact technical specification, module interfaces, and implementation blueprint for:
1. `C:\OsintNeoAi\workspaces\osintneoai_indexer\extractors\ocr_engine.py`:
   - RapidOCR ONNX integration (`rapidocr_onnxruntime`), lazy model initialization, multi-page generator, bounding box and confidence filtering.
   - Strict memory management: explicit pixmap destruction (`del pix; del img_np`) and garbage collection.
2. `C:\OsintNeoAi\workspaces\osintneoai_indexer\extractors\image_enhancer.py`:
   - OpenCV CLAHE (Contrast Limited Adaptive Histogram Equalization), adaptive Otsu/Gaussian thresholding, deskewing, and noise reduction for degraded/faxed scans.
3. `C:\OsintNeoAi\workspaces\osintneoai_indexer\extractors\document_extractor.py` (Core Extraction Ladder):
   - 5-Tier Fallback Ladder: Digital PyMuPDF -> Density Check -> 300 DPI Rendering + RapidOCR -> OpenCV CLAHE Enhancement -> Fallback to raw text.

Deliverables:
- Write detailed implementation plan and code specifications to `C:\OsintNeoAi\.agents\explorer_m2_1\analysis.md`
- Write 5-component handoff report to `C:\OsintNeoAi\.agents\explorer_m2_1\handoff.md`
- Send completion message to parent orchestrator.
