-- BigQuery Master Evidence Relational Cross-Referencing Query
-- Project: noble-beanbag-497411-m4
-- Targets: 32 Master Target Accounts vs 3,510 SHA-256 Forensic Ledgers

WITH target_accounts AS (
  SELECT email FROM UNNEST([
    'amd949609@dimarcello949.onmicrosoft.com', 'amd949609@gmail.com', 'amd@dimarcello.net', 'anthony.dimarcello.student@gmail.com', 'anthony.dimarcello.student@outlook.com', 'anthony.dimarcello@students.post.edu', 'anthony@dimarcello.net', 'anthony@dimarcello949.com', 'anthonymd949@gmail.com', 'anthonymichaeldimarcello@gmail.com', 'atlasoccustomcabinets@gmail.com', 'ceo@anthonydimarcellonet.com', 'contact@anthonydimarcello.net', 'disoledesign@gmail.com', 'drillingoilandgasinfo@gmail.com', 'geoffreycarlyenutt@gmail.com', 'gmd949609@gmail.com', 'ironmandavinci@gmail.com', 'johnyrocketoc@gmail.com', 'makeitsoxo@gmail.com', 'michaelsiringo0@gmail.com', 'mistresskaylabdsm@gmail.com', 'my4angels1984@gmail.com', 'need2bfunky1@gmail.com', 'osintneoai@gmail.com', 'pmportal949@gmail.com', 'rolandgallardo714@gmail.com', 'sunsetmaverick949@gmail.com', 'tradingt3@gmail.com', 'txtdjdrop@gmail.com', 'txtdjdrop@outlook.com', 'wccinfo909@gmail.com'
  ]) AS email
),
evidence_ledger AS (
  SELECT 
    sha256,
    file_name,
    file_path,
    created_time,
    size_bytes,
    'onedrive_forensics' AS source_dataset
  FROM `noble-beanbag-497411-m4.onedrive_forensics.onedrive_documents`
  UNION ALL
  SELECT 
    sha256,
    file_name,
    file_path,
    created_time,
    size_bytes,
    'national_audits' AS source_dataset
  FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
)
SELECT 
  t.email AS target_account,
  e.sha256,
  e.file_name,
  e.file_path,
  e.source_dataset,
  e.created_time
FROM evidence_ledger e
CROSS JOIN target_accounts t
WHERE LOWER(e.file_path) LIKE CONCAT('%', LOWER(t.email), '%')
   OR LOWER(e.file_name) LIKE CONCAT('%', LOWER(t.email), '%')
ORDER BY e.created_time DESC;
