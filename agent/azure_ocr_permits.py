"""
azure_ocr_permits.py — OCR 687 permit PDFs via Azure Document Intelligence + pipe to BigQuery.
Requires: azure_config.json or AZURE_DOC_INTEL_ENDPOINT / AZURE_DOC_INTEL_KEY env vars.
Run: python azure_ocr_permits.py
"""
import os, json, sys, time
from google.cloud import bigquery
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azure_config.json")
alt = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\azure_config.json"

config = {}
for p in [config_path, alt]:
    if os.path.exists(p):
        with open(p) as f: config = json.load(f); break

endpoint = config.get("doc_intel_endpoint") or os.environ.get("AZURE_DOC_INTEL_ENDPOINT")
key = config.get("doc_intel_key") or os.environ.get("AZURE_DOC_INTEL_KEY")
PROJECT = "project-743aab84-f9a5-4ec7-954"
MANIFEST = r"C:\Users\HP\OneDrive\Documents\opencode_work\permit_backups_manifest.txt"

if not endpoint or not key:
    print("Azure Document Intelligence not configured. Run azure_setup.py --provision first.")
    sys.exit(1)

client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
bq = bigquery.Client(project=PROJECT)

# Ensure BigQuery table exists
table_id = f"{PROJECT}.ai_sandbox.permit_ocr_results"
try:
    bq.get_table(table_id)
except:
    from google.cloud.bigquery import SchemaField, Table
    schema = [
        SchemaField("file_path", "STRING"),
        SchemaField("filename", "STRING"),
        SchemaField("page_count", "INTEGER"),
        SchemaField("extracted_text", "STRING"),
        SchemaField("key_value_count", "INTEGER"),
        SchemaField("ocr_timestamp", "TIMESTAMP"),
    ]
    bq.create_table(Table(table_id, schema=schema))
    print(f"Created {table_id}")

# Load manifest
with open(MANIFEST, 'r', encoding='utf-8', errors='ignore') as f:
    files = [line.strip() for line in f if line.strip().lower().endswith('.pdf')]

print(f"=== Azure Document Intelligence — OCR {len(files)} PDFs ===\n")

count = 0
errors = 0
for file_path in files:
    if not os.path.exists(file_path): continue
    if count >= 100:  # limit per run to avoid costs
        print(f"Reached {count} limit. Restart to continue.")
        break
    
    filename = os.path.basename(file_path)
    try:
        with open(file_path, 'rb') as f:
            poller = client.begin_analyze_document("prebuilt-read", document=f)
            result = poller.result()
        
        text = " ".join([line.content for page in result.pages for line in page.lines])[:50000]
        kv_count = len(result.key_value_pairs)
        
        # Save to BigQuery
        bq.query(f"""
            INSERT INTO `{table_id}` (file_path, filename, page_count, extracted_text, key_value_count, ocr_timestamp)
            VALUES (@path, @name, @pages, @text, @kvs, CURRENT_TIMESTAMP())
        """, job_config=bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("path", "STRING", file_path),
            bigquery.ScalarQueryParameter("name", "STRING", filename),
            bigquery.ScalarQueryParameter("pages", "INTEGER", len(result.pages)),
            bigquery.ScalarQueryParameter("text", "STRING", text),
            bigquery.ScalarQueryParameter("kvs", "INTEGER", kv_count),
        ])).result()
        
        count += 1
        print(f"  [{count}] {filename[:50]} — {len(result.pages)} pages, {len(text)} chars, {kv_count} KVs")
    except Exception as e:
        errors += 1
        if errors <= 5: print(f"  ERROR: {filename[:60]} — {e}")

print(f"\nDone. Processed: {count}, Errors: {errors}")
print(f"BigQuery table: {table_id}")
