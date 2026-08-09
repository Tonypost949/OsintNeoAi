from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== mat_looker_forensic_base ===")
rows = client.query("""
    SELECT * FROM `noble-beanbag-497411-m4.national_audits.mat_looker_forensic_base`
    ORDER BY total_homeless_count DESC, leakage_delta DESC
""").result()
for row in rows:
    print(f"{row.state_anchor}: audits={row.active_audits}, homeless={row.total_homeless_count}, unsheltered={row.total_unsheltered_count}, CoC funding=${row.total_coc_funding}, target={row.corporate_target}, billing={row.clinic_billing_id}, leakage={row.leakage_delta}, hazard={row.hazard_site}, toxic={row.toxic_severity_multiplier}")

print("\n=== all_state_records for CA ===")
rows = client.query("""
    SELECT state, total_performance_audits, last_updated_at,
           non_profiteers_index
    FROM `noble-beanbag-497411-m4.national_audits.all_state_records`
    WHERE state = 'CA'
""").result()
for row in rows:
    print(f"State: {row.state}, Audits: {row.total_performance_audits}, Updated: {row.last_updated_at}")
    print(f"Non-profiteers: {row.non_profiteers_index}")

print("\n=== Search gmail_index for HB/church/PPP keywords ===")
rows = client.query("""
    SELECT subject, sender, recipient, snippet, date_header
    FROM `noble-beanbag-497411-m4.national_audits.gmail_index`
    WHERE REGEXP_CONTAINS(UPPER(CONCAT(subject, ' ', snippet)), r'HUNTINGTON|CHURCH|PPP|DELAWARE|MAIN ST|BETTER FUTURE|BWB SURF')
    LIMIT 20
""").result()
for row in rows:
    print(f"{row.date_header} | {row.sender} -> {row.recipient}")
    print(f"  Subject: {row.subject}")
    print(f"  Snippet: {row.snippet}")
    print()
