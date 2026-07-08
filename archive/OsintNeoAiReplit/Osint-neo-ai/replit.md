# OSINT AI Neo

## Overview

OSINT AI Neo is a comprehensive Open Source Intelligence (OSINT) platform built with Streamlit. It provides target enumeration, entity tracking, file/folder scanning, NLP analysis, social media intelligence, and a local master intelligence sheet — all in a dark cyberpunk-themed dashboard.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend & Application Framework
- **Framework:** Streamlit (multi-page, modular architecture)
- **Theme:** Custom dark cyberpunk CSS matching the OSINT Neo AI design (`#0a0e1a` background, `#00d4ff` accent)
- **Visualization:** Plotly Express for charts, Folium (via `streamlit-folium`) for interactive geolocation maps
- **Layout:** Wide layout with dark sidebar navigation and Capability Index

### Application Pages
1. **Dashboard (`pages/dashboard.py`)** — Live metrics, entity geolocation map (CartoDB dark_matter tiles), risk distribution pie chart, entity type bar chart, events timeline
2. **Target Enumeration (`pages/target_enum.py`)** — IP, domain, and phone scanning with auto-detect; WHOIS integration; results saved to SQLite + displayed as JSON; scan history
3. **Master Sheet (`pages/master_sheet.py`)** — Full CRUD for entities, relationships, events; tabbed interface; color-coded risk levels; Excel export with download
4. **File & Folder Scanner (`pages/file_scanner_page.py`)** — Scans any local directory recursively; extracts image EXIF/GPS data, audio metadata, contact VCF, text previews; progress bar; notable findings highlight
5. **NLP Analysis (`pages/nlp_analysis.py`)** — Pattern-based entity extraction (emails, phones, IPs, URLs, dates, money, SSNs, case numbers, legal/financial/threat keywords); confidence scoring; saves high-confidence entities to DB
6. **Social Media (`pages/social_media.py`)** — Multi-platform username search (Twitter, Instagram, LinkedIn, GitHub, Reddit, etc.); profile grid display; saves to master DB

### Data Layer
- **Database:** SQLite (`data/osint_master.db`) via `utils/database.py`
  - Tables: `entities`, `relationships`, `events`, `scan_results`, `file_scan_results`
  - Pre-seeded with sample OSINT data on first run
- **Master Sheet:** Excel workbook (`data/OSINT_Master_Sheet.xlsx`) via `utils/excel_gen.py`
  - Sheets: Summary, Entities, Relationships, Events, File Scans, Target Scans
  - Color-coded risk levels, frozen headers, professional formatting

### Utilities
- `utils/database.py` — SQLite connection, CRUD operations, seeding, stats
- `utils/excel_gen.py` — openpyxl-based Excel generation with dark styling
- `utils/file_scanner.py` — Recursive directory walker; EXIF via Pillow; audio metadata via Mutagen; VCF contact parser; MD5 hashing

## External Dependencies

### Python Packages
- **streamlit** — Core web framework
- **pandas** — Data manipulation and display
- **plotly** — Interactive charts
- **folium + streamlit-folium** — Interactive geo maps
- **openpyxl** — Excel master sheet generation
- **Pillow** — Image EXIF metadata extraction
- **mutagen** — Audio file metadata extraction
- **python-whois** — Domain WHOIS lookups
- **requests** — HTTP for future API integrations

### APIs & Services (Future Integration)
- IP geolocation: ipinfo.io, Shodan
- Phone lookup: NumVerify, Twilio Lookup
- Social media: Twitter/X API, Instagram Graph API, GitHub API
- NLP/LLM: spaCy multilingual, Hugging Face NER, Google NLP API
- Threat feeds: AbuseIPDB, VirusTotal
