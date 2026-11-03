---
name: notebooklm-extract
description: Extracts, parses, and ingests NotebookLM HTML exports, sources, notes, and Studio artifacts into structured markdown and JSON datasets.
---

# NotebookLM Extraction & Ingestion Skill

Autonomous extractor for Google NotebookLM exports and saved HTML sessions.

## Execution

Execute the standalone ingest engine:
```powershell
python C:\Amd949609_Antigravity_v1\tools\notebooklm_ingest_tool.py
```

Or run text extraction and cloud sync:
```powershell
python C:\Amd949609_Antigravity_v1\scripts\extract_notebooks.py
```

## Features
- Ingests NotebookLM files from `Downloads` or `C:\OsintNeoAi\data\chats\notebooks`
- Extracts Studio artifacts (Audio overviews, Study Guides, Mind Maps, Outlines)
- Extracts Document Sources and Notes
- Compiles master index to `C:\OsintNeoAi\data\notebooklm_master_sources_index.json`

