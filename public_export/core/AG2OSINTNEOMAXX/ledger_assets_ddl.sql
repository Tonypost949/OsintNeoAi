-- Ledger Assets — BigQuery table for investigation-scoped threat hunting
-- Every asset has a page on the ledger. Hunter scans urls/ips on that page (not user PC)
-- Run: bq query --project_id=noble-beanbag-497411-m4 < ledger_assets_ddl.sql
-- or: python ledger_hunter.py --ensure-table --text "test"

CREATE SCHEMA IF NOT EXISTS `noble-beanbag-497411-m4.forensic_layers`
OPTIONS(location="US", description="Ledger + forensic hunting");

CREATE TABLE IF NOT EXISTS `noble-beanbag-497411-m4.forensic_layers.ledger_assets` (
  asset_id STRING NOT NULL OPTIONS(description="ledger asset page id"),
  title STRING OPTIONS(description="asset page title"),
  ledger_page STRING OPTIONS(description="page path or ledger reference"),
  text STRING OPTIONS(description="full page text / OCR up to 100k"),
  urls ARRAY<STRING> OPTIONS(description="extracted http/https urls"),
  ips ARRAY<STRING> OPTIONS(description="extracted public ips (private filtered)"),
  domains ARRAY<STRING> OPTIONS(description="extracted bare domains"),
  ioc_count INT64 OPTIONS(description="len(urls)+len(ips)"),
  threat_hunt_status STRING OPTIONS(description="Queued/Running/Completed/Failed/Skipped"),
  determination STRING OPTIONS(description="Substantial Evidence / Evidence Found / Threat Not Found / Pending"),
  hunt_summary STRING OPTIONS(description="human summary"),
  evidence JSON OPTIONS(description="hits + TI enrichment"),
  hunt_queries ARRAY<STRING> OPTIONS(description="BigQuery YL2->SQL queries run"),
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  hunt_completed_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY asset_id
OPTIONS(description="Ledger assets - hunter scans urls/ips on page against investigation data only");

-- Verify
SELECT table_name, ddl FROM `noble-beanbag-497411-m4.forensic_layers.INFORMATION_SCHEMA.TABLES` WHERE table_name='ledger_assets';
