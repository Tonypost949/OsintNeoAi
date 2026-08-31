## 2026-08-29T17:41:00Z

You are Explorer 3 for Milestone 1 (M1: Ingestion & Streaming Engine) of the OsintNeoAi Indexer project.
Your Working Directory: C:\OsintNeoAi\.agents\explorer_m1_3\

Authoritative Context:
- Project Plan: C:\OsintNeoAi\PROJECT.md
- User Request: C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md (## 2026-08-29T17:34:35Z)
- User Rules & Backups: C:\OsintNeoAi\AGENTS.md
- Prior Survey Analysis: C:\OsintNeoAi\.agents\explorer_survey_1\analysis.md and C:\OsintNeoAi\.agents\explorer_survey_2\analysis.md

Your Task:
Investigate and design the exact technical specification, module interfaces, and implementation blueprint for:
1. `C:\OsintNeoAi\workspaces\osintneoai_indexer\connectors\gdrive_streamer.py`:
   - Google Drive URL parser (extracts file ID from `drive.google.com/file/d/{id}`, `drive.google.com/open?id={id}`, `docs.google.com/document/d/{id}/export?format=pdf`, etc.).
   - Streaming downloader using `urllib.request` / `requests` with 64 KB chunk buffers, automatic virus-scan confirmation token handling (`confirm=t` / cookies), and fallback to local mirrored cache if offline.
   - Yields `IngestedArtifact` dataclass instances.
2. `C:\OsintNeoAi\workspaces\osintneoai_indexer\connectors\mailbox_reader.py`:
   - Streaming MBOX and EML reader using standard library `mailbox.mbox` and `email` packages.
   - Iterates through messages with zero memory bloat, decodes RFC 2047 MIME headers (Subject, From, To, Date), extracts plaintext / HTML bodies and attachments, and computes SHA-256 for each email record and attachment.
   - Yields `IngestedArtifact` dataclass instances.

Deliverables:
- Write detailed implementation plan and code specifications to `C:\OsintNeoAi\.agents\explorer_m1_3\analysis.md`
- Write 5-component handoff report to `C:\OsintNeoAi\.agents\explorer_m1_3\handoff.md`
- Send completion message to parent orchestrator.
