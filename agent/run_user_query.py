import os
from google.cloud import bigquery

# 1. Append CSS classes
css_content = """
.hidden { display: none; }
.spacer { flex: 1; }
.hidden-input { display: none; }
.upload-status { margin-top: 12px; font-size: 13px; color: var(--text-muted); }
"""
with open(r'c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\static\style.css', 'a') as f:
    f.write(css_content)
print("CSS classes appended.")

# 2. Run BigQuery query
client = bigquery.Client()
query = """
SELECT 
  matches.value AS target_indicator,
  matches.type AS indicator_type,
  failures.id AS failure_node_id,
  failures.created_at AS failure_timestamp,
  SUBSTR(failures.contents_raw, 1, 500) AS failure_context
FROM 
  `project-743aab84-f9a5-4ec7-954.national_audits.local_scan_matches` AS matches
JOIN 
  `project-743aab84-f9a5-4ec7-954.national_audits.orange_county_structural_failure` AS failures
ON 
  LOWER(failures.contents_raw) LIKE CONCAT('%', LOWER(matches.value), '%')
WHERE 
  matches.type IN ('Phone', 'Email', 'Name')
LIMIT 50;
"""
try:
    print("Running query...")
    query_job = client.query(query)
    results = query_job.result()
    print("Query results:")
    for row in results:
        print(f"Indicator: {row['target_indicator']} ({row['indicator_type']})")
        print(f"Node ID: {row['failure_node_id']}")
        print(f"Timestamp: {row['failure_timestamp']}")
        print(f"Context: {row['failure_context']}")
        print("-" * 40)
except Exception as e:
    print(f"Query error: {e}")
