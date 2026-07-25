# Walkthrough - OSINT & NPI Integration Complete

All 16 backup repositories have been successfully processed, extracted, and fully integrated. We have upgraded your Streamlit dashboard (`osint_dashboard.py`) to connect directly to the massive **Riconow Graph Database** and perform **Non-Profiteers Index (NPI) Forensic Auditing** on-demand.

## Key Accomplishments

### 1. Unified Archive Parity & Extraction
- All 16 `.zip` files under `github_backups/` are monitored and synchronized by `sync_backups.py`.
- Run `python sync_backups.py` at any point to verify or extract updates dynamically.

### 2. Live Riconow Network Graph Explorer
- Connects directly to `riconow/Tonypost949-riconow-f7bfe00/AG2OSINTNEOMAXX/nodes.json` and `edges.json`.
- Visualizes the relational connections between **17,807 nodes** and **18,705 edges** using an optimized 2-hop spring layout.
- Search nodes by name, ID, address, or property, and inspect their adjacent neighbors with rich interactive Plotly maps.

### 3. Non-Profiteers Index (NPI) Forensic Tab
- Built a forensic audit dashboard implementing the AAR, ODR, and NPI formulas.
- Fully automated red flag checking for government dependency, asset storage, and direct service rates.
- Includes preloaded presets for:
  - **Viet America Society** (Andrew Do / Peter Pham case indicia)
  - **Bright Future Nonprofit Inc** (from `business_workbook.xlsx`)
  - **Healthy Community Foundation** (control sample)

---

## How to Run

Launch the dashboard locally with:
```powershell
streamlit run osint_dashboard.py
```
This will open the upgraded interactive suite in your browser, where you can explore the network and execute audits instantly!
