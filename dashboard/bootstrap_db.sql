-- Create Dataset
CREATE SCHEMA IF NOT EXISTS `national_audits`;

-- Create Main Audit Table
CREATE TABLE IF NOT EXISTS `national_audits.all_state_records` (
  state_code STRING,
  non_profiteers_index ARRAY<STRUCT<npi_id STRING, organization_name STRING, cms_billing_code STRING, unaccounted_fund_delta FLOAT64>>,
  environmental_site_assessments ARRAY<STRUCT<location_name STRING, contaminant_type STRING, test_multiplier FLOAT64>>
);

-- Create Audit Trail
CREATE TABLE IF NOT EXISTS `national_audits.ingestion_audit_trail` (
  state_code STRING,
  ingestion_timestamp TIMESTAMP,
  status STRING,
  rows_ingested INT64,
  error_message STRING
);

-- Create Minutes Table
CREATE TABLE IF NOT EXISTS `national_audits.city_council_minutes` (
  parcel_id STRING,
  meeting_date DATE,
  statement STRING,
  municipality STRING,
  state_code STRING
);

-- Create Risk Scoring View
CREATE OR REPLACE VIEW `national_audits.entity_risk_scoring` AS
SELECT 
    state_code,
    npi.organization_name,
    npi.unaccounted_fund_delta,
    CASE 
        WHEN npi.unaccounted_fund_delta >= 1000000000 THEN 'CRITICAL: Systemic Liability'
        WHEN npi.unaccounted_fund_delta >= 10000000 THEN 'HIGH: Procurement Capture'
        WHEN npi.unaccounted_fund_delta > 0 THEN 'MEDIUM: Oversight Drift'
        ELSE 'LOW: Monitor'
    END as risk_tier
FROM `national_audits.all_state_records`,
UNNEST(non_profiteers_index) as npi;
