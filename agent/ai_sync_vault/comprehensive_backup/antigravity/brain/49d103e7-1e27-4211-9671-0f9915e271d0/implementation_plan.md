# Implementation Plan - OSINT & NPI Integration & Autopilot Synchronization

This plan integrates the **Non-Profiteers Index (NPI)** methodology and the massive **Riconow Graph Database** (17,807 nodes, 18,705 edges) from your backup repositories into your primary OSINT Intelligence Suite and Streamlit Dashboard. It also establishes a background synchronization scheduler to automatically check for updates to `riconow.zip` and re-ingest data.

## User Review Required

> [!IMPORTANT]
> - We will be integrating a real-time database loader for the 17.8k nodes and 18.7k edges from `riconow` directly into your Streamlit Dashboard.
> - An automatic background sync script `sync_backups.py` will be created to monitor zip updates in `github_backups/` and extract them on the fly.
> - We will add a dedicated **NPI Forensic Auditing** screen to the dashboard to calculate risk scores for all non-profits and GNOs.

## Proposed Changes

### Core System & Synchronization

#### [NEW] [sync_backups.py](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/sync_backups.py)
Create a synchronization script that:
- Scans `github_backups/` for updates to `riconow.zip` and `NPI---Non-Profiteers-Index.zip`.
- Automatically extracts new zips to keep the local folders up to date.
- Provides a clean API for other modules to reload graph data when changed.

### OSINT Intelligence Dashboard

#### [MODIFY] [osint_dashboard.py](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/osint_dashboard.py)
Upgrade the Streamlit dashboard to:
1. **Load Real Riconow Data**: Parse the unzipped `nodes.json` and `edges.json` from the `riconow` folder to populate the Network Analysis tab with real-world entities (replacing the static dummy graph).
2. **Implement Interactive Entity Search**: Allow searching the 17,807 nodes and exploring their active connections.
3. **Incorporate NPI Forensic Audit screen**: A dedicated module that lists GNOs/nonprofits, computes their Asset Accumulation Ratios (AAR), Overhead Distortion Ratios (ODR), and final NPI Scores, and highlights structural red flags.

## Verification Plan

### Automated Tests
- Run `sync_backups.py` to ensure it successfully detects and handles extraction.
- Run `streamlit run osint_dashboard.py` to verify the dashboard can load, filter, and render thousands of nodes and run forensic calculations.
