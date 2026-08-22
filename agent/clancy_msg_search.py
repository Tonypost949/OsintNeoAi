from google.cloud import bigquery

client = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== SEARCHING BIGQUERY DATASETS FOR CLANCY / ZOLOFT ===")

queries = {
    "deepseek_conversations": """
        SELECT 'deepseek_conversations' as source, title as subject, messages_raw as snippet, create_time as date
        FROM `noble-beanbag-497411-m4.national_audits.deepseek_conversations`
        WHERE UPPER(messages_raw) LIKE '%CLANCY%' OR UPPER(messages_raw) LIKE '%ZOLOFT%'
        LIMIT 10
    """,
    "local_scan_emails": """
        SELECT 'local_scan_emails' as source, 'Email content' as subject, email as snippet, '' as date
        FROM `noble-beanbag-497411-m4.national_audits.local_scan_emails`
        WHERE UPPER(email) LIKE '%CLANCY%' OR UPPER(email) LIKE '%ZOLOFT%'
        LIMIT 10
    """,
    "takeout_documents": """
        SELECT 'takeout_documents' as source, file_name as subject, extracted_text as snippet, CAST(ingest_timestamp AS STRING) as date
        FROM `noble-beanbag-497411-m4.national_audits.takeout_documents`
        WHERE UPPER(extracted_text) LIKE '%CLANCY%' OR UPPER(extracted_text) LIKE '%ZOLOFT%'
        LIMIT 10
    """,
    "onedrive_documents": """
        SELECT 'onedrive_documents' as source, file_name as subject, content_preview as snippet, CAST(ingestion_timestamp AS STRING) as date
        FROM `noble-beanbag-497411-m4.onedrive_forensics.onedrive_documents`
        WHERE UPPER(content_preview) LIKE '%CLANCY%' OR UPPER(content_preview) LIKE '%ZOLOFT%'
        LIMIT 10
    """
}

for name, q in queries.items():
    print(f"\n--- Querying {name} ---")
    try:
        results = list(client.query(q).result())
        print(f"Found {len(results)} matches:")
        for r in results:
            src = r.get('source')
            subj = r.get('subject', '')
            snip = r.get('snippet', '')
            dt = r.get('date', '')
            print(f"  [{src}] Date: {dt} | Subject: {subj}\n    Snippet: {snip[:400]}...")
    except Exception as e:
        print(f"Error querying {name}: {e}")

print("\nSearch complete.")
