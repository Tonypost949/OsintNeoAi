# Implementation Plan - NPI Pipeline Operationalization & Anomaly Monitoring

We will weaponize the NPI pipeline to continuously monitor, track, and alert on local Orange County (OC) control clusters that serve as funnels for national HUD/CoC grants. This plan outlines the technical approach to loading our extensive graph data into BigQuery and setting up real-time anomaly alerts within the Aegis correlation engine.

## Technical Design & Approach

### 1. Schema Extensions & Table Creations
We will extend the BigQuery schema inside project `project-743aab84-f9a5-4ec7-954` under the `npi_forensic` dataset to support the relational address mapping and continuous alert logging:
*   **New Junction Table**: `npi_forensic.entity_addresses`
    *   `entity_id` (STRING, REQUIRED)
    *   `address_id` (STRING, REQUIRED)
    *   `address_string` (STRING)
    *   `ingestion_timestamp` (TIMESTAMP)
*   **New Alert Log Table**: `npi_forensic.alerts_flagged`
    *   `alert_id` (STRING, REQUIRED)
    *   `timestamp` (TIMESTAMP, REQUIRED)
    *   `category` (STRING, REQUIRED) — e.g., 'ADDRESS_CLUSTER', 'DEGREE_ANOMALY', 'CROSS_JURISDICTION'
    *   `severity` (STRING) — 'CRITICAL', 'WARNING'
    *   `details` (STRING) — JSON payload describing the anomalous entities, persons, or hubs.

### 2. Graph-to-BigQuery Bulk Loader
We will build a high-performance Python utility (`bulk_load_graph_to_bq.py`) that reads `nodes.json` and `edges.json` from our active workspace and loads them into BigQuery:
*   Extracts all `ORGANIZATION` nodes and populates `npi_forensic.entities` (3,843 nodes).
*   Extracts all `PERSON` nodes and populates `npi_forensic.nodes_person` (3,208 nodes).
*   Extracts all `OFFICER_OF` / control relationships and populates `npi_forensic.edges_officer_of`.
*   Resolves `ORGANIZATION` registered addresses and locations, populating the new `npi_forensic.entity_addresses` table.

### 3. Integrated Threat Monitoring inside Aegis Engine
We will update the Aegis Correlation Engine (`aegis_correlation_engine.py`) to execute the three forensic queries as part of its verification and monitoring loop:
1.  **Address Cluster Monitor**: Identifies new out-of-state entities registering to known OC hubs.
2.  **Hub Degree Centrality Anomaly**: Flags individuals whose control network spikes abnormally relative to historical averages.
3.  **Cross-Jurisdiction Funnel Tracker**: Maps out-of-state/national entities back to Orange County control clusters.

All triggered anomalies will be printed to the terminal with high-visibility ANSI styling and saved persistently to `npi_forensic.alerts_flagged`.

---

## Proposed Changes

### Database Layer
#### [NEW] [entity_addresses](file:///project-743aab84-f9a5-4ec7-954:npi_forensic.entity_addresses) (BigQuery Table)
#### [NEW] [alerts_flagged](file:///project-743aab84-f9a5-4ec7-954:npi_forensic.alerts_flagged) (BigQuery Table)

### Bulk Loading Utility
#### [NEW] [bulk_load_graph_to_bq.py](file:///C:/Users/HP/OneDrive/Documents/AG2OSINTNEOMAXX/bulk_load_graph_to_bq.py)
*   Translates and populates all 17,000+ local graph components to BigQuery.

### Monitoring Engine
#### [MODIFY] [aegis_correlation_engine.py](file:///C:/Users/HP/OneDrive/Documents/AG2OSINTNEOMAXX/aegis_correlation_engine.py)
*   Integrate continuous BigQuery monitoring alerts.
*   Log triggered alerts to `npi_forensic.alerts_flagged`.

---

## Verification Plan

### Automated Tests
1.  **Dry Run**: Validate BQ queries against local schema definitions.
2.  **Execution**: Run `python bulk_load_graph_to_bq.py` to ingest local graph data.
3.  **Alert Validation**: Run `python aegis_correlation_engine.py` and inspect triggered alerts in the terminal and inside the `alerts_flagged` table.

### Manual Verification
*   Verify that `entity_addresses` contains matching records and maps successfully to known address hubs like `11770 WARNER AVE STE 215`.
*   Validate alert outputs inside `alerts_flagged` table.
