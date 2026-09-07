CREATE TABLE `your-project-id.osint_engine.master_ledger` (
  -- 1. Cryptographic Identity & Lineage (The Bitcoin Mechanics)
  asset_hash STRING NOT NULL OPTIONS(description="SHA-256 point-of-upload hash to guarantee file integrity"),
  parent_hash STRING OPTIONS(description="References previous block hash for data ancestry / UTXO tracking"),
  miner_signature STRING NOT NULL OPTIONS(description="Submitter's verified crypto wallet address"),

  -- 2. Multi-Ledger Routing (The Tagging Engine)
  domain_tags ARRAY<STRING> OPTIONS(description="Nested array for multi-routing e.g., ['OSINT', 'TAX-FUNDED']"),

  -- 3. The Evidence / Metadata Payload
  title STRING NOT NULL,
  description STRING,
  raw_payload_uri STRING OPTIONS(description="Pointer to physical file in Azure Blob or IPFS"),
  
  -- 4. Event Sourcing / Append-Only Guardrails
  version_id INT64 NOT NULL OPTIONS(description="Sequential version layer to prevent pointer corruption"),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() OPTIONS(description="Timestamp of block creation"),
  is_active BOOLEAN DEFAULT TRUE OPTIONS(description="False if updated, preserving historical record")
)
PARTITION BY DATE(created_at)
CLUSTER BY domain_tags, miner_signature;

