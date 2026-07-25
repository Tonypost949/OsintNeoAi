# Task List - Continuous Anomaly Pipeline Operationalization

- [x] Create/Extend BigQuery schemas and tables
    - [x] Create `entity_addresses` table schema
    - [x] Create `alerts_flagged` log table schema
- [x] Create graph-to-BigQuery bulk loading utility (`bulk_load_graph_to_bq.py`)
    - [x] Load organizations into `entities`
    - [x] Load persons into `nodes_person`
    - [x] Load officer relationships into `edges_officer_of`
    - [x] Extract and load address associations into `entity_addresses`
- [x] Implement detection and monitoring queries in `aegis_correlation_engine.py`
    - [x] Add `address_cluster_monitor` alert logic
    - [x] Add `hub_degree_anomaly` alert logic
    - [x] Add `cross_jurisdiction_funnel` alert logic
    - [x] Save triggered alerts persistently to `alerts_flagged`
- [x] Validate and run the complete continuous monitoring loop
