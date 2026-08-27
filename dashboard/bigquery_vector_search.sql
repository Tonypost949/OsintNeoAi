-- ==============================================================================
-- PIPELINE 1: SEMANTIC VECTOR SEARCH & EMBEDDING RETRIEVAL
-- Target Project: noble-beanbag-497411-m4
-- Dataset: forensic_ml
-- ==============================================================================

-- Step 1: Ensure ML schema exists
CREATE SCHEMA IF NOT EXISTS 
oble-beanbag-497411-m4.forensic_ml;

-- Step 2: Create Vertex AI Remote Embedding Model
CREATE OR REPLACE MODEL 
oble-beanbag-497411-m4.forensic_ml.text_embedding_model
REMOTE WITH CONNECTION DEFAULT
OPTIONS (
  ENDPOINT = 'text-embedding-005'
);

-- Step 3: Materialize Embeddings for Discovery Evidence & Documents
CREATE OR REPLACE TABLE 
oble-beanbag-497411-m4.forensic_ml.document_embeddings AS
SELECT
  d.file_id,
  d.file_name,
  d.mime_type,
  d.web_view_link,
  d.description,
  ml_output.embedding AS text_embedding
FROM
  
oble-beanbag-497411-m4.national_audits.drive_file_index AS d,
  AI.GENERATE_EMBEDDING(
    MODEL 
oble-beanbag-497411-m4.forensic_ml.text_embedding_model,
    (SELECT COALESCE(d.description, d.file_name) AS content)
  ) AS ml_output
WHERE
  d.file_name IS NOT NULL;

-- Step 4: Semantic Query Retrieval via VECTOR_SEARCH TVF
SELECT
  query.search_term AS target_investigation,
  base.file_id,
  base.file_name,
  base.web_view_link,
  ROUND(1 - distance, 4) AS cosine_similarity_score
FROM
  VECTOR_SEARCH(
    TABLE 
oble-beanbag-497411-m4.forensic_ml.document_embeddings,
    'text_embedding',
    (
      SELECT
        content AS search_term,
        embedding
      FROM
        AI.GENERATE_EMBEDDING(
          MODEL 
oble-beanbag-497411-m4.forensic_ml.text_embedding_model,
          (
            SELECT "Surplus Land Act AB 1486  HCD Notice of Violation Angel Stadium" AS content
            UNION ALL
            SELECT "1601 Dove Street Suite 145 HOMI Helping Of Mentally Ill Experienc 8 Lakeview" AS content
            UNION ALL
            SELECT "Perjured Form UD-101 Box 7d(2) triple default ROA #26 #51 #60 CCP 473(d)" AS content
            UNION ALL
            SELECT "17631 Cameron Lane hexavalent chromium plume GeoTracker tampering Yamada" AS content
          )
        )
    ),
    top_k => 5,
    distance_type => 'COSINE'
  )
ORDER BY
  target_investigation, cosine_similarity_score DESC;
