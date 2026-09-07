import os
from google.cloud import bigquery

def run_queries():
    gcp_project_id = "noble-beanbag-497411-m4"
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
    LIMIT 25
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
    LIMIT 25
    """
    
    print("[*] Executing Priority 3: Environmental-Financial Nexus...")
    try:
        results_3 = client.query(query_3).result()
        p3_output = "\n".join([f"- Site: {row.site_id} | Location: {row.location_name} | Toxic Multiplier: {row.test_multiplier}x | Associated Org: {row.organization_name} | Fund Leakage: ${row.unaccounted_fund_delta}" for row in results_3])
    except Exception as e:
        p3_output = f"ERROR executing Priority 3: {e}"

    print("[*] Executing Priority 4: Individual Financial Fingerprinting...")
    try:
        results_4 = client.query(query_4).result()
        p4_output = "\n".join([f"- NPI ID: {row.npi_id} | Organization: {row.organization_name} | Shell Intel Link: {row.opencorporates_url} | OSINT Trace: {row.truthfinder_link}" for row in results_4])
    except Exception as e:
        p4_output = f"ERROR executing Priority 4: {e}"

    artifact_content = f"""# Forensic Execution Results

## Priority 3: Environmental-Financial Nexus
{p3_output if p3_output else "No anomalies detected."}

## Priority 4: Individual Financial Fingerprinting
{p4_output if p4_output else "No shell registrations detected."}
"""
    
    artifact_dir = os.environ.get("ANTIGRAVITY_ARTIFACT_DIR", r"C:\Users\Amd949609\.gemini\antigravity\brain\5bb23128-3893-4550-8276-247611692a41")
    os.makedirs(artifact_dir, exist_ok=True)
    artifact_path = os.path.join(artifact_dir, "forensic_results.md")
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write(artifact_content)
    
    print(f"[*] Results saved to {artifact_path}")
    print("\n" + "="*50)
    print(artifact_content)
    print("="*50)

if __name__ == "__main__":
    run_queries()
