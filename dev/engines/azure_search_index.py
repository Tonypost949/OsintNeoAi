"""
azure_search_index.py — Index BigQuery gmail_index + drive_file_index into Azure AI Search.
Requires: azure_config.json (from azure_setup.py) or env vars.
Run: python azure_search_index.py
"""
import os, json, sys
from google.cloud import bigquery

# Load config
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azure_config.json")
alt_config = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\azure_config.json"

config = {}
for p in [config_path, alt_config]:
    if os.path.exists(p):
        with open(p) as f: config = json.load(f); break

endpoint = config.get("search_endpoint") or os.environ.get("AZURE_SEARCH_ENDPOINT")
key = config.get("search_key") or os.environ.get("AZURE_SEARCH_KEY")
PROJECT = "noble-beanbag-497411-m4"

if not endpoint or not key:
    print("Azure Search not configured. Run azure_setup.py --provision first.")
    print("Or set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY env vars.")
    sys.exit(1)

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType,
    VectorSearch, HnswParameters, HnswAlgorithmConfiguration,
    SearchField, VectorSearchAlgorithmMetric
)

credential = AzureKeyCredential(key)
index_client = SearchIndexClient(endpoint, credential)

# --- GMAIL INDEX ---
gmail_schema = [
    SimpleField("id", SearchFieldDataType.String, key=True),
    SearchableField("subject", SearchFieldDataType.String, analyzer="en.microsoft"),
    SearchableField("sender", SearchFieldDataType.String),
    SearchableField("snippet", SearchFieldDataType.String, analyzer="en.microsoft"),
    SimpleField("date_header", SearchFieldDataType.String, filterable=True, sortable=True),
    SimpleField("thread_id", SearchFieldDataType.String, filterable=True),
]

gmail_index = SearchIndex(
    name="gmail-index",
    fields=gmail_schema,
    vector_search=VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw", parameters=HnswParameters(metric=VectorSearchAlgorithmMetric.COSINE))]
    )
)

print("=== Indexing Gmail (30K emails) into Azure AI Search ===")

try:
    index_client.create_or_update_index(gmail_index)
    print("  gmail-index schema created")
except Exception as e:
    print(f"  gmail-index: {e}")

bq = bigquery.Client(project=PROJECT)

# Upload gmail data to search
from azure.search.documents import SearchClient
gmail_client = SearchClient(endpoint, "gmail-index", credential)

q_gmail = """SELECT message_id, thread_id, subject, sender, date_header, snippet, label_ids FROM `noble-beanbag-497411-m4.national_audits.gmail_index` LIMIT 30000"""
print("  Pulling gmail data from BigQuery...")
batch = []
count = 0
for row in bq.query(q_gmail):
    doc = {
        "id": str(row.message_id),
        "thread_id": str(row.thread_id or ''),
        "subject": str(row.subject or '')[:500],
        "sender": str(row.sender or '')[:200],
        "snippet": str(row.snippet or '')[:1000],
        "date_header": str(row.date_header or ''),
    }
    batch.append(doc)
    if len(batch) >= 200:
        gmail_client.upload_documents(batch)
        count += len(batch)
        print(f"  Indexed {count} emails...")
        batch = []

if batch:
    gmail_client.upload_documents(batch)
    count += len(batch)
print(f"  Gmail index complete: {count} documents")

# --- DRIVE FILE INDEX ---
drive_schema = [
    SimpleField("id", SearchFieldDataType.String, key=True),
    SearchableField("file_name", SearchFieldDataType.String, analyzer="en.microsoft"),
    SearchableField("mime_type", SearchFieldDataType.String),
    SearchableField("owner_emails", SearchFieldDataType.String),
    SimpleField("created_time", SearchFieldDataType.String, filterable=True, sortable=True),
    SimpleField("size_bytes", SearchFieldDataType.Int64, filterable=True, sortable=True),
    SimpleField("is_shared", SearchFieldDataType.Boolean, filterable=True),
]

drive_index = SearchIndex(name="drive-index", fields=drive_schema)

print("\n=== Indexing Drive Files (359K documents) ===")
try:
    index_client.create_or_update_index(drive_index)
except Exception as e:
    print(f"  drive-index: {e}")

drive_client = SearchClient(endpoint, "drive-index", credential)
q_drive = """SELECT file_id, file_name, mime_type, owner_emails, created_time, size_bytes, is_shared, web_view_link FROM `noble-beanbag-497411-m4.national_audits.drive_file_index` WHERE NOT is_trashed ORDER BY created_time DESC LIMIT 50000"""
print("  Pulling drive file data from BigQuery...")
batch = []
count = 0
for row in bq.query(q_drive):
    doc = {
        "id": str(row.file_id),
        "file_name": str(row.file_name or '')[:300],
        "mime_type": str(row.mime_type or '')[:100],
        "owner_emails": str(row.owner_emails or '')[:300],
        "created_time": str(row.created_time or ''),
        "size_bytes": int(row.size_bytes or 0),
        "is_shared": bool(row.is_shared),
    }
    batch.append(doc)
    if len(batch) >= 200:
        drive_client.upload_documents(batch)
        count += len(batch)
        print(f"  Indexed {count} files...")
        batch = []
if batch:
    drive_client.upload_documents(batch)
    count += len(batch)
print(f"  Drive index complete: {count} documents")

# Save index stats
stats_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azure_search_stats.json")
with open(stats_path, 'w') as f:
    json.dump({"gmail_indexed": count, "drive_indexed": count, "timestamp": str(bq.query("SELECT CURRENT_TIMESTAMP() AS now").result().__iter__().__next__().now)}, f)
print(f"\nDone. Stats saved to {stats_path}")
