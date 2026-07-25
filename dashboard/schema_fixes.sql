CREATE TABLE IF NOT EXISTS `noble-beanbag-497411-m4.national_audits.ingestion_audit_trail` (
  state_code STRING, 
  ingestion_timestamp TIMESTAMP, 
  status STRING, 
  rows_ingested INT64, 
  error_message STRING
); 

CREATE TABLE IF NOT EXISTS `noble-beanbag-497411-m4.national_audits.city_council_minutes` (
  parcel_id STRING, 
  meeting_date DATE, 
  statement STRING, 
  municipality STRING, 
  state_code STRING
);
