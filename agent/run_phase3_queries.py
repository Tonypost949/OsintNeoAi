import os
from google.cloud import bigquery

def run_queries():
    gcp_project_id = "project-743aab84-f9a5-4ec7-954"
    client = bigquery.Client(project=gcp_project_id)
    
    # 1. IIM Trust Fund Depth Probe
    query_1 = f"""
    SELECT 
      npi.organization_name, 
      npi.unaccounted_fund_delta,
      npi.task_tracking_url
    FROM `{gcp_project_id}.national_audits.all_state_records`,
    UNNEST(non_profiteers_index) AS npi
    WHERE npi.organization_name LIKE '%IIM%' 
       OR npi.organization_name LIKE '%BTFA%'
       OR npi.organization_name LIKE '%Bureau of Trust Funds%'
       OR npi.task_tracking_url LIKE '%IIM%'
       OR npi.task_tracking_url LIKE '%BTFA%'
    """

    # 2. Cross-State Correlative Analysis (AZ, VA)
    query_2 = f"""
    SELECT 
      state,
      npi.organization_name, 
      npi.opencorporates_url,
      npi.unaccounted_fund_delta
    FROM `{gcp_project_id}.national_audits.all_state_records`,
    UNNEST(non_profiteers_index) AS npi
    WHERE state IN ('AZ', 'VA')
      AND npi.unaccounted_fund_delta > 0
    """

    # 4. Procurement Audit Sweeps (Che LLC, Shigeru Yamada, HBNC)
    query_4 = f"""
    SELECT 
      state,
      npi.organization_name,
      npi.opencorporates_url,
      npi.unaccounted_fund_delta
    FROM `{gcp_project_id}.national_audits.all_state_records`,
    UNNEST(non_profiteers_index) AS npi
    WHERE npi.organization_name LIKE '%Che LLC%' 
       OR npi.organization_name LIKE '%Shigeru Yamada%'
       OR npi.organization_name LIKE '%Mercy House%'
    """
    
    output = []
    
    print("[*] Executing Probe 1: IIM Trust Fund Depth Probe...")
    try:
        results = client.query(query_1).result()
        res_list = [f"- Org: {row.organization_name} | Fund Delta: ${row.unaccounted_fund_delta} | Tracking URL: {row.task_tracking_url}" for row in results]
        output.append("## 1. IIM Trust Fund Depth Probe\\n" + ("\\n".join(res_list) if res_list else "No IIM/BTFA blind spot routing detected in current matrix."))
    except Exception as e:
        output.append(f"## 1. IIM Trust Fund Depth Probe\\nERROR: {e}")

    print("[*] Executing Probe 2: Cross-State Correlative Analysis (AZ, VA)...")
    try:
        results = client.query(query_2).result()
        res_list = [f"- State: {row.state} | Org: {row.organization_name} | Shell Intel Link: {row.opencorporates_url} | Fund Delta: ${row.unaccounted_fund_delta}" for row in results]
        output.append("## 2. Cross-State Correlative Analysis\\n" + ("\\n".join(res_list) if res_list else "No proxy connections mapped in AZ or VA."))
    except Exception as e:
        output.append(f"## 2. Cross-State Correlative Analysis\\nERROR: {e}")

    print("[*] Executing Probe 4: Procurement Sweeps (HBNC Corporate Leads)...")
    try:
        results = client.query(query_4).result()
        res_list = [f"- State: {row.state} | Target: {row.organization_name} | Shell Intel: {row.opencorporates_url} | Risk / Delta: ${row.unaccounted_fund_delta}" for row in results]
        output.append("## 3. Procurement Audit Sweeps (HBNC Target Anchors)\\n" + ("\\n".join(res_list) if res_list else "No transactional alignments detected for Che LLC or Shigeru Yamada."))
    except Exception as e:
        output.append(f"## 3. Procurement Audit Sweeps (HBNC Target Anchors)\\nERROR: {e}")

    artifact_content = "# Phase 3 OSINT Execution Logs\\n\\n" + "\\n\\n".join(output)
    
    artifact_path = os.path.join(r"C:\Users\HP\.gemini\antigravity-ide\brain\3a3fb7d5-104a-4ef7-8ddb-1d08eb64b1f5", "phase3_results.md")
    with open(artifact_path, "w") as f:
        f.write(artifact_content)
    
    print(f"[*] Results saved to {artifact_path}")

if __name__ == "__main__":
    run_queries()
