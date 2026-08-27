-- ==============================================================================
-- PIPELINE 3: AUTOMATED EVIDENCE CLASSIFICATION & ENTITY SYNTHESIS
-- Target Project: noble-beanbag-497411-m4
-- Datasets: national_audits, forensic_layers
-- ==============================================================================

-- 1. Multi-Vector Classification via AI.CLASSIFY
SELECT
  file_id,
  file_name AS document_name,
  mime_type,
  web_view_link,
  AI.CLASSIFY(
    COALESCE(description, file_name),
    categories => [
      'FCA_False_Claims_Act',
      'Surplus_Land_Act_AB1486',
      'Unlawful_Detainer_Eviction_Fraud',
      'CEQA_Environmental_Endangerment',
      'Public_Corruption_RICO'
    ],
    output_mode => 'multi',
    endpoint => 'gemini-2.5-flash'
  ) AS statutory_violation_vectors
FROM
  
oble-beanbag-497411-m4.national_audits.drive_file_index
WHERE
  file_name IS NOT NULL
LIMIT 100;
