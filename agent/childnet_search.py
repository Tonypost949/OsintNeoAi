from google.cloud import bigquery

client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

print("=== SEARCHING DOCUMENTS FOR CHILDNET & PRESCRIBERS ===")

q = """SELECT file_name, file_path, extracted_text
FROM `project-743aab84-f9a5-4ec7-954.national_audits.takeout_documents`
WHERE UPPER(file_name) LIKE '%CHILDNET%' 
   OR UPPER(file_name) LIKE '%FRAUD%' 
   OR UPPER(extracted_text) LIKE '%CHILDNET%'
   OR UPPER(extracted_text) LIKE '%PRESCRIB%'"""

results = list(client.query(q).result())
print(f"Found {len(results)} matches:")
for r in results:
    text = r['extracted_text'] or ""
    # Look for ChildNet or prescriber lines specifically to display
    lines = text.split('\n')
    matching_lines = [l.strip() for l in lines if 'CHILDNET' in l.upper() or 'PRESCRIB' in l.upper() or 'ANGULO' in l.upper()][:20]
    print(f"\nDocument: {r['file_name']} ({r['file_path']})")
    print("Sample Matching Lines:")
    for ml in matching_lines:
        print(f"  {ml}")
