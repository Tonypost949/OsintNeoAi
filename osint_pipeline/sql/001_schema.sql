-- 001_schema.sql — BigQuery schema for OSINT pipeline
-- Run once in BigQuery console or via bq query

CREATE TABLE IF NOT EXISTS `{project}.{dataset}.entities` (
    entity_id STRING NOT NULL,
    entity_name STRING NOT NULL,
    entity_type STRING,           -- LLC, CORPORATION, LP, etc.
    entity_number STRING,         -- CA SOS entity number
    status STRING,                -- ACTIVE, DISSOLVED, SUSPENDED
    state STRING,                 -- CA, NV, etc.
    filing_date DATE,
    registered_agent STRING,
    agent_address STRING,
    mail_address STRING,
    source STRING,                -- ca_sos, bq_ppp, manual
    confidence_score FLOAT64,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    metadata JSON
)
PARTITION BY DATE(first_seen)
CLUSTER BY entity_type, state, status;

CREATE TABLE IF NOT EXISTS `{project}.{dataset}.relationships` (
    relationship_id STRING NOT NULL,
    source_entity_id STRING NOT NULL,
    target_entity_id STRING NOT NULL,
    relationship_type STRING NOT NULL,  -- owns, registered_agent, same_address, same_agent, loan_to
    weight FLOAT64 DEFAULT 1.0,
    evidence JSON,                       -- supporting data points
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(first_seen)
CLUSTER BY relationship_type, source_entity_id;

CREATE TABLE IF NOT EXISTS `{project}.{dataset}.filings` (
    filing_id STRING NOT NULL,
    entity_number STRING NOT NULL,
    filing_type STRING,
    filing_date DATE,
    document_title STRING,
    image_url STRING,
    source STRING DEFAULT 'ca_sos',
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(filing_date);

CREATE TABLE IF NOT EXISTS `{project}.{dataset}.attorneys` (
    attorney_id STRING NOT NULL,
    bar_number STRING,
    name STRING NOT NULL,
    firm_name STRING,
    address STRING,
    city STRING,
    state STRING DEFAULT 'CA',
    phone STRING,
    email STRING,
    entity_count INT64 DEFAULT 0,
    total_loan_amount FLOAT64 DEFAULT 0.0,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY state, entity_count;

CREATE TABLE IF NOT EXISTS `{project}.{dataset}.people` (
    person_id STRING NOT NULL,
    full_name STRING NOT NULL,
    aliases ARRAY<STRING>,
    addresses ARRAY<STRING>,
    phone_numbers ARRAY<STRING>,
    emails ARRAY<STRING>,
    linked_entities ARRAY<STRING>,    -- entity_ids
    linked_llc_count INT64 DEFAULT 0,
    total_ppp_amount FLOAT64 DEFAULT 0.0,
    source STRING,                    -- nexis, ca_sos, manual
    confidence_score FLOAT64,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS `{project}.{dataset}.control_cluster` (
    cluster_id STRING NOT NULL,
    root_entity_id STRING NOT NULL,
    entity_ids ARRAY<STRING>,
    person_ids ARRAY<STRING>,
    total_entities INT64,
    total_loan_amount FLOAT64,
    geographic_span ARRAY<STRING>,    -- states involved
    risk_score FLOAT64,               -- 0-100
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
