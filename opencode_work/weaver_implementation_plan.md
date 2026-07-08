# Load Forensic PPP Loans into BigQuery

We are going to load the forensic results for STEWART INDUSTRIES LLC and TRIUMVIRATE LLC into the BigQuery dataset `forensic_layers` for cross-referencing.

## Proposed Changes

### [NEW] [load_forensic_layers.py](file:///c:/Users/HP/.gemini/antigravity-ide/scratch/osint-agent/load_forensic_layers.py)
This script creates the dataset and table if they do not exist, and inserts the structured records into BigQuery.

## Verification Plan

### Automated Tests
- Run `load_forensic_layers.py` and verify successful ingestion output.
