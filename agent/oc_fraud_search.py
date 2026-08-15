from google.cloud import bigquery

client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')

print("=== EXTRACTING OC FRAUD NETWORK REPORT V13 CONTENTS ===")

q = """SELECT file_name, file_path, extracted_text
FROM `project-743aab84-f9a5-4ec7-954.national_audits.takeout_documents`
WHERE UPPER(file_name) LIKE '%OC_FRAUD_NETWORK_OSINT_REPORT_V13%'"""

results = list(client.query(q).result())
if results:
    print(f"Found {len(results)} match(es). Printing contents:")
    # We print the first 4000 characters of the extracted text containing ChildNet / prescribers.
    text = results[0]['extracted_text'] or ""
    # Find position of ChildNet or prescriber to print context
    pos = text.upper().find("CHILDNET")
    if pos != -1:
        start = max(0, pos - 500)
        end = min(len(text), pos + 3500)
        print(text[start:end])
    else:
        print(text[:4000])
else:
    print("No direct match found for the V13 report file name. Trying broader search...")
    # Broader search for Childnet Youth And Family Services
    q2 = """SELECT file_name, extracted_text 
            FROM `project-743aab84-f9a5-4ec7-954.national_audits.takeout_documents`
            WHERE UPPER(extracted_text) LIKE '%CHILDNET%' LIMIT 3"""
    r2 = list(client.query(q2).result())
    for r in r2:
        print(f"\n--- Document: {r['file_name']} ---")
        text = r['extracted_text'] or ""
        pos = text.upper().find("CHILDNET")
        print(text[max(0, pos-200):min(len(text), pos+1500)])
