import os
from google.cloud import bigquery

def run_queries():
    gcp_project_id = "project-743aab84-f9a5-4ec7-954"
    client = bigquery.Client(project=gcp_project_id)
    
    # Priority 3: Environmental-Financial Nexus
    query_3 = f"""
    WITH ESA_Data AS (
      SELECT 
        state, 
        esa.site_id, 
        esa.test_multiplier, 
        esa.location_name 
      FROM `{gcp_project_id}.national_audits.all_state_records`,
      UNNEST(environmental_site_assessments) AS esa
    ),
    NPI_Data AS (
      SELECT 
        state, 
        npi.npi_id, 
        npi.organization_name, 
        npi.unaccounted_fund_delta 
      FROM `{gcp_project_id}.national_audits.all_state_records`,
      UNNEST(non_profiteers_index) AS npi
    )
    SELECT 
      E.site_id, 
      E.location_name, 
      E.test_multiplier, 
      N.organization_name, 
      N.unaccounted_fund_delta 
    FROM ESA_Data E
    JOIN NPI_Data N ON E.state = N.state
    WHERE E.state = 'CA'
    """
    
    # Priority 4: Individual Financial Fingerprinting
    query_4 = f"""
    SELECT 
      npi.npi_id, 
      npi.organization_name, 
      npi.opencorporates_url, 
      npi.truthfinder_link 
    FROM `{gcp_project_id}.national_audits.all_state_records`,
    UNNEST(non_profiteers_index) AS npi
    WHERE state = 'CA' 
      AND (npi.organization_name LIKE '%Che LLC%' 
           OR npi.organization_name LIKE '%Mercy House%'
           OR npi.organization_name LIKE '%Viet America%')
    """
    
    print("[*] Executing Priority 3: Environmental-Financial Nexus...")
    try:
        results_3 = client.query(query_3).result()
        p3_output = "\\n".join([f"- Site: {row.site_id} | Location: {row.location_name} | Toxic Multiplier: {row.test_multiplier}x | Associated Org: {row.organization_name} | Fund Leakage: ${row.unaccounted_fund_delta}" for row in results_3])
    except Exception as e:
        p3_output = f"ERROR executing Priority 3: {e}"

    print("[*] Executing Priority 4: Individual Financial Fingerprinting...")
    try:
        results_4 = client.query(query_4).result()
        p4_output = "\\n".join([f"- NPI ID: {row.npi_id} | Organization: {row.organization_name} | Shell Intel Link: {row.opencorporates_url} | OSINT Trace: {row.truthfinder_link}" for row in results_4])
    except Exception as e:
        p4_output = f"ERROR executing Priority 4: {e}"

    artifact_content = f"""# Forensic Execution Results

## Priority 3: Environmental-Financial Nexus
{p3_output if p3_output else "No anomalies detected."}

## Priority 4: Individual Financial Fingerprinting
{p4_output if p4_output else "No shell registrations detected."}
"""
    
    artifact_path = os.path.join(r"C:\Users\HP\.gemini\antigravity-ide\brain\3a3fb7d5-104a-4ef7-8ddb-1d08eb64b1f5", "forensic_results.md")
    with open(artifact_path, "w") as f:
        f.write(artifact_content)
    
    print(f"[*] Results saved to {artifact_path}")

if __name__ == "__main__":
    run_queries()
