from google.cloud import bigquery

client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

print("=== SEARCHING EMAILS & DOCUMENTS FOR FAKE PRESCRIPTIONS / MEDICAL FRAUD ===")

queries = {
    "gmail_index_prescriptions": """
        SELECT 'gmail_index' as source, subject, snippet, date_header as date
        FROM `project-743aab84-f9a5-4ec7-954.national_audits.gmail_index`
        WHERE UPPER(subject) LIKE '%PRESCRIPTION%' OR UPPER(snippet) LIKE '%PRESCRIPTION%'
           OR UPPER(subject) LIKE '%PHARMACY%' OR UPPER(snippet) LIKE '%PHARMACY%'
           OR UPPER(subject) LIKE '% CLINIC%' OR UPPER(snippet) LIKE '% CLINIC%'
           OR UPPER(subject) LIKE '%DOCTOR%' OR UPPER(snippet) LIKE '%DOCTOR%'
           OR UPPER(subject) LIKE '%MEDICAL FRAUD%' OR UPPER(snippet) LIKE '%MEDICAL FRAUD%'
           OR UPPER(subject) LIKE '% FAKE%' OR UPPER(snippet) LIKE '% FAKE%'
        ORDER BY date_header DESC
        LIMIT 20
    """,
    "takeout_documents_prescriptions": """
        SELECT 'takeout_documents' as source, file_name as subject, extracted_text as snippet, '' as date
        FROM `project-743aab84-f9a5-4ec7-954.national_audits.takeout_documents`
        WHERE UPPER(extracted_text) LIKE '%PRESCRIPTION%' 
           OR UPPER(extracted_text) LIKE '%PHARMACY%'
           OR UPPER(extracted_text) LIKE '%MEDICAL FRAUD%'
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
            print(f"  [{src}] Date: {dt} | Subject: {subj}\n    Snippet: {snip[:450]}...")
    except Exception as e:
        print(f"Error querying {name}: {e}")

print("\nSearch complete.")
