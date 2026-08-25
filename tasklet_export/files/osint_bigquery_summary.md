# OSINT / BigQuery Investigation Summary

**Saved locally:** `C:\Users\HP\OneDrive\Documents\osint_bigquery_summary.md`  
**Target cloud path:** `gs://osint-ai-evidence-vault-m4/pc_backup/osint_bigquery_summary.md`

---

## Goal
- Cross-reference BigQuery datasets to trace municipal RICO/financial disbursement patterns against environmental compliance timelines for target properties.

## Constraints & Preferences
- Bypass local UI or browser crashes by running raw SQL and Cloud Shell `bq` commands directly against BigQuery.
- Preserve exact project IDs, dataset names, and addresses.

## Progress
### Done
- Verified BigQuery connection to Google Cloud project `noble-beanbag-497411-m4`.
- Listed active datasets: `ai_sandbox`, `hb_church_osint`, `national_audits`, `nppes_export`, `ppp_rico`.
- Mapped dataset purposes:
  - `ppp_rico`: financial tracing (loan patterns, shell companies, forgiveness anomalies)
  - `hb_church_osint`: local property / historical land use
  - `nppes_export` / `national_audits`: identity and entity cross-reference
  - `ai_sandbox`: staging / validation
- Identified target addresses: `17642 Beach Blvd`, `17631 Cameron Ln`.
- Identified target entities: RPM Team, Mercy House.
- Drafted SQL cross-correlation query joining `noble-beanbag-497411-m4.ppp_rico.loan_records` and `noble-beanbag-497411-m4.national_audits.california_compliance`.
- Provided `bq load` command template for `noble-beanbag-497411-m4:ppp_rico.municipal_disbursements`.

### In Progress
- Awaiting selection of next table schema or data sequence to run through the BigQuery console.

### Blocked
- (none)

## Key Decisions
- Use the BigQuery console / Cloud Shell SDK as the primary interface to avoid local frontend instability.

## Next Steps
- Select and execute the next table schema or data sequence through the BigQuery console.

## Critical Context
- **Google Cloud project ID:** `noble-beanbag-497411-m4`
- **Active gcloud account:** `txtdjdrop@gmail.com`
- **⚠️ SENSITIVE — OAuth authorization code (treat as secret):**
  ```
  4/0AdkVLPy_Uk8o2JILdrZP6F6z2KCkvjJGzG6iZro5Nhx39Ms_WEBvnGHbjA3zFdZ6xNPy4A
  ```
  This code should be rotated/revoked after use and never shared in plain text.
- **Assumed/proposed table schemas:**
  - `noble-beanbag-497411-m4.ppp_rico.loan_records`
  - `noble-beanbag-497411-m4.national_audits.california_compliance`
  - `noble-beanbag-497411-m4.ppp_rico.municipal_disbursements`
  Their actual existence has not been independently verified.
- **Violation delta calculation:** `ceqa_exemption_date - contamination_log_date`

## Reference Queries

### Forensic Cross-Correlation
```sql
SELECT 
    ppp.corporate_name,
    ppp.loan_amount,
    ppp.forgiveness_date,
    audit.ceqa_exemption_date,
    audit.contamination_log_date,
    (audit.ceqa_exemption_date - audit.contamination_log_date) AS violation_days_delta
FROM 
    `noble-beanbag-497411-m4.ppp_rico.loan_records` AS ppp
JOIN 
    `noble-beanbag-497411-m4.national_audits.california_compliance` AS audit
ON 
    ppp.entity_id = audit.entity_id
WHERE 
    audit.site_address IN ('17642 Beach Blvd', '17631 Cameron Ln')
    AND audit.contamination_log_date <= audit.ceqa_exemption_date;
```

### CSV Ingest Template
```bash
bq load --source_format=CSV --skip_leading_rows=1 \
  noble-beanbag-497411-m4:ppp_rico.municipal_disbursements \
  ./local_staging_ledger.csv
```

## Relevant Files
- `C:\Users\HP\OneDrive\Documents\osint_bigquery_summary.md` (this file)
