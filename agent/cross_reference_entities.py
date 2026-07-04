import os
import re
from google.cloud import bigquery

LOCAL_DIR = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent"
GCP_PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
BQ_TABLE = f"{GCP_PROJECT_ID}.national_audits.all_state_records"

def extract_local_entities(directory):
    print(f"[*] Scanning local directory: {directory} for entity vectors...")
    entity_patterns = [
        re.compile(r'\b[A-Za-z0-9&-]+\s+LLC\b', re.IGNORECASE),
        re.compile(r'\b(Stewart|Triumvirate|Mercy House|Childnet|Sterling-Rivers)\b', re.IGNORECASE)
    ]
    extracted_entities = set()
    
    if not os.path.exists(directory):
        print(f"[-] Directory {directory} not found.")
        return list()
        
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.txt', '.md', '.csv', '.json')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in entity_patterns:
                            for match in pattern.finditer(content):
                                extracted_entities.add(match.group(0).strip())
                except Exception as e:
                    pass
                    
    print(f"[+] Extracted {len(extracted_entities)} unique entities from local files.")
    return list(extracted_entities)

def cross_reference_with_bigquery(entities):
    print("[*] Contacting BigQuery cluster for cross-state verification...")
    if not entities:
        print("[-] No entities extracted. Aborting BQ verification.")
        return

    client = bigquery.Client(project=GCP_PROJECT_ID)
    
    # Batch entities to avoid huge queries
    batch_size = 50
    matches_found = 0
    
    for i in range(0, len(entities), batch_size):
        batch = entities[i:i+batch_size]
        query_conditions = []
        query_params = []
        
        for j, entity in enumerate(batch):
            param_name = f"entity_{i}_{j}"
            query_conditions.append(f"LOWER(npi.organization_name) LIKE @{param_name}")
            query_params.append(bigquery.ScalarQueryParameter(param_name, "STRING", f"%{entity.lower()}%"))
            
        sql_query = f"""
        SELECT 
            state,
            npi.organization_name,
            npi.cms_billing_code,
            npi.unaccounted_fund_delta
        FROM `{BQ_TABLE}`,
        UNNEST(non_profiteers_index) as npi
        WHERE {" OR ".join(query_conditions)}
        """
        
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        
        try:
            query_job = client.query(sql_query, job_config=job_config)
            results = list(query_job.result())
            
            for row in results:
                matches_found += 1
                print(f" [!] MATCH FOUND [{row.state}]")
                print(f"     └─ Entity: {row.organization_name}")
                print(f"     └─ Billing Code: {row.cms_billing_code}")
                print(f"     └─ Unaccounted Delta: ${float(row.unaccounted_fund_delta):,.2f}\n")
        except Exception as e:
            print(f"[-] BigQuery execution failed for batch: {e}")
            
    print(f"[+] Scan completed. {matches_found} cross-state vectors confirmed.")

if __name__ == '__main__':
    local_entities = extract_local_entities(LOCAL_DIR)
    # Only check top 20 to save time and API quota, sort alphabetically
    cross_reference_with_bigquery(sorted(local_entities)[:20])
