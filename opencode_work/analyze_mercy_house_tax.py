import os
import sys
import json
from google.cloud import bigquery
from google import genai
from google.genai import types

sys.stdout.reconfigure(encoding="utf-8")

GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "noble-beanbag-497411-m4")
BQ_DATASET = "national_audits"
PDF_PATH = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7\2022-MERCY_HOUSE_PUBLIC_RETURN.pdf"

def analyze_pdf_directly(pdf_path):
    print(f"Reading raw PDF bytes from: {pdf_path}")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
        
    print("Uploading inline PDF bytes to Gemini for forensic OCR and analysis...")
    ai_client = genai.Client(vertexai=True, project=GCP_PROJECT, location="us-central1")
    
    prompt = """
    You are OSINTNeoAi, a forensic data auditor. Below is the full scanned PDF of the Form 990 public tax return of Mercy House Living Centers.
    Please analyze the visual tables in this PDF and extract the following exact metrics:
    1. Fiscal Year End / Tax Year
    2. Total Revenue (Form 990 Part I, Line 12 or Part VIII, Line 12h/12)
    3. Total Expenses (Form 990 Part I, Line 18 or Part IX, Line 25)
    4. Net Assets or Fund Balances (Form 990 Part I, Line 22 or Part X, Line 33)
    5. Discrepancies, executive compensation, or significant fund flows.
    
    Calculate the 'unaccounted_fund_delta' as the difference or unexplained outflow if any, or specify the total federal/state/municipal grant funding received if it's the primary target of auditing.
    
    Return ONLY a JSON block with this exact format (no markdown, no backticks, no comments):
    {
        "organization_name": "Mercy House Living Centers",
        "fiscal_year": "<year, e.g., 2022>",
        "total_revenue": <float or null>,
        "total_expenses": <float or null>,
        "net_assets": <float or null>,
        "unaccounted_fund_delta": <float value of the calculated discrepancy or the revenue if suspicious>,
        "assessment": "<detailed summary of findings, including exact revenue and expenses discovered>"
    }
    """
    
    pdf_part = types.Part.from_bytes(
        data=pdf_bytes,
        mime_type="application/pdf"
    )
    
    try:
        response = ai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[pdf_part, prompt]
        )
        res_text = response.text.replace('```json', '').replace('```', '').strip()
        parsed = json.loads(res_text)
        return parsed
    except Exception as e:
        print(f"Gemini generation error: {e}")
        return None

def inject_to_bigquery(finding):
    print("Injecting true Mercy House metrics into BigQuery...")
    client = bigquery.Client(project=GCP_PROJECT)
    
    query = f"""
        UPDATE `{GCP_PROJECT}.{BQ_DATASET}.all_state_records`
        SET non_profiteers_index = ARRAY_CONCAT(IFNULL(non_profiteers_index, []), [
          STRUCT(
            @cms_code AS npi_id, 
            @org_name AS organization_name, 
            CAST(NULL AS STRING) AS opencorporates_url,
            @cms_code AS cms_billing_code, 
            CAST(NULL AS STRING) AS truthfinder_link,
            @assessment AS task_tracking_url,
            CAST(@delta AS NUMERIC) AS unaccounted_fund_delta
          )
        ])
        WHERE state = 'CA'
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("cms_code", "STRING", f"MERCY-HOUSE-TAX-FY{finding.get('fiscal_year', '2022')}"),
            bigquery.ScalarQueryParameter("org_name", "STRING", finding["organization_name"]),
            bigquery.ScalarQueryParameter("delta", "FLOAT64", float(finding["unaccounted_fund_delta"])),
            bigquery.ScalarQueryParameter("assessment", "STRING", finding["assessment"]),
        ]
    )
    
    try:
        client.query(query, job_config=job_config).result()
        print("Success: BigQuery Update Complete!")
    except Exception as e:
        print(f"Error: BigQuery update failed: {e}")

def main():
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF not found at {PDF_PATH}")
        return
        
    finding = analyze_pdf_directly(PDF_PATH)
    
    if finding:
        print("\n--- GEMINI OSINT FORENSIC REPORT ---")
        print(json.dumps(finding, indent=2))
        print("------------------------------------\n")
        inject_to_bigquery(finding)
    else:
        print("Failed to get analysis from Gemini.")

if __name__ == "__main__":
    main()
