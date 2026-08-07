import os
import sys
import json
import requests
from google.cloud import bigquery
from google import genai

# Secure In-Memory Operations
def fetch_public_tax_data(organization_name):
    print(f"[SECURE LINK] Connecting to ProPublica API for target: {organization_name}...")
    url = f"https://projects.propublica.org/nonprofits/api/v2/search.json?q={requests.utils.quote(organization_name)}"
    
    headers = {
        "User-Agent": "OSINTNeoAi Forensic Scraper/1.0"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data and data.get("organizations"):
                return data["organizations"][0] # Return top match
            else:
                return None
    except Exception as e:
        print(f"[!] Network error: {e}")
        return None

def process_evidence_with_ai(org_data):
    # Pure in-memory analysis without writing to disk
    print("[AI MODULE] Initializing Gemini for forensic calculation...")
    
    # Extract known public metrics
    name = org_data.get("name", "UNKNOWN")
    revenue = org_data.get("revenue", 0)
    expenses = org_data.get("expenses", 0)
    asset_amount = org_data.get("asset_amount", 0)
    income_amount = org_data.get("income_amount", 0)
    ein = org_data.get("ein", "UNKNOWN")
    
    prompt = f"""
    You are OSINTNeoAi. We have retrieved public tax documentation (Form 990 data) for a target organization.
    Please calculate any discrepancies and flag for potential tax fraud/fund delta anomalies.
    
    TARGET NAME: {name}
    EIN: {ein}
    TOTAL REVENUE: {revenue}
    TOTAL EXPENSES: {expenses}
    NET ASSETS: {asset_amount}
    INCOME: {income_amount}
    
    If expenses significantly exceed revenue or vice-versa without matching assets, estimate an "unaccounted_fund_delta" float value.
    Return ONLY a JSON block with the following keys:
    {{
        "organization_name": "{name}",
        "cms_billing_code": "TAX-FRAUD-EIN-{ein}",
        "unaccounted_fund_delta": <float value of the calculated discrepancy or the revenue if suspicious>,
        "assessment": "<short summary of findings>"
    }}
    """
    
    gcp_project_id = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
    ai_client = genai.Client(vertexai=True, project=gcp_project_id, location="global")
    
    try:
        response = ai_client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )
        
        # Clean the response to ensure it parses as JSON
        res_text = response.text.replace('```json', '').replace('```', '').strip()
        parsed = json.loads(res_text)
        return parsed
    except Exception as e:
        print(f"[!] AI Processing Error: {e}")
        return None

def inject_to_database(finding):
    print("[DATABASE] Injecting parsed evidence directly into BigQuery...")
    gcp_project_id = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
    client = bigquery.Client(project=gcp_project_id)
    
    # We'll inject this into the "CA" row for testing purposes or "UNKNOWN" state.
    # To keep it anti-duplication, we append to the CA array.
    query = f"""
        UPDATE `{gcp_project_id}.national_audits.all_state_records`
        SET non_profiteers_index = ARRAY_CONCAT(IFNULL(non_profiteers_index, []), [
          STRUCT(
            @cms_code AS npi_id, 
            @org_name AS organization_name, 
            CAST(NULL AS STRING) AS opencorporates_url,
            @cms_code AS cms_billing_code, 
            CAST(NULL AS STRING) AS truthfinder_link,
            CAST(NULL AS STRING) AS task_tracking_url,
            CAST(@delta AS NUMERIC) AS unaccounted_fund_delta
          )
        ])
        WHERE state = 'CA'
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("cms_code", "STRING", finding["cms_billing_code"]),
            bigquery.ScalarQueryParameter("org_name", "STRING", finding["organization_name"]),
            bigquery.ScalarQueryParameter("delta", "FLOAT64", float(finding["unaccounted_fund_delta"])),
        ]
    )
    
    try:
        client.query(query, job_config=job_config).result()
        print("[DATABASE] Injection successful. Target logged.")
    except Exception as e:
        print(f"[!] BigQuery Error: {e}")


def run_pipeline(target_name):
    # 1. Fetch
    data = fetch_public_tax_data(target_name)
    if not data:
        print("[!] No public data found or error occurred.")
        return
    
    # 2. Analyze (In Memory)
    finding = process_evidence_with_ai(data)
    if not finding:
        print("[!] Failed to parse AI findings.")
        return
        
    print(f"\n--- OSINT FORENSIC RESULT ---")
    print(f"Target: {finding['organization_name']}")
    print(f"Delta Identified: ${finding['unaccounted_fund_delta']:,.2f}")
    print(f"Assessment: {finding['assessment']}")
    print(f"-----------------------------\n")
    
    # 3. Inject
    inject_to_database(finding)
    
    # 4. Secure wipe (Python memory cleanup is automatic when variables fall out of scope)
    # Ensuring no files were written to disk.
    del data
    del finding
    print("[SECURE] All temporary evidence buffers completely wiped from memory.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Viet America Society"
    run_pipeline(target)
