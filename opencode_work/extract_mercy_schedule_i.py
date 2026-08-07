import os, json
from google.cloud import bigquery
from google import genai
from google.genai import types

GCP_PROJECT = "noble-beanbag-497411-m4"
BQ_DATASET = "national_audits"
PDF_PATH = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7\2022-MERCY_HOUSE_PUBLIC_RETURN.pdf"

def extract_schedule_i(pdf_path):
    print("Reading Mercy House 990 PDF...")
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    print("Sending to Gemini for Schedule I / federal awards extraction...")
    ai_client = genai.Client(vertexai=True, project=GCP_PROJECT, location="global")

    prompt = """
    You are a forensic auditor analyzing the Form 990 public tax return of Mercy House Living Centers.

    Focus specifically on:
    - Schedule I: Grants and Other Assistance to Organizations, Governments, and Individuals in the United States
    - Any federal awards / grants breakdown sections
    - Part VIII revenue lines showing government grants
    - Any footnotes or audit findings mentioning misclassified grants or a $1.5M misstatement

    Extract EVERY grant/award entry with:
    - Grantor/agency name
    - Program name (CDBG, ESG, HOME, HUD, CARES Act, ARPA, HHAP, etc.)
    - Amount received
    - Fiscal year
    - Grant ID, contract number, or award number (if visible)
    - Whether it was a pass-through from another entity
    - Any notes about misclassification or restatement

    Return ONLY a JSON block with this exact structure (no markdown, no backticks, no comments):
    {
        "organization_name": "Mercy House Living Centers",
        "fiscal_year": "2022",
        "total_government_grants": 51011265.0,
        "misclassified_grant_amount": 1500000.0,
        "misclassification_notes": "<summary if found>",
        "grants": [
            {
                "grantor_name": "<name>",
                "program_name": "<program>",
                "amount": <float>,
                "grant_id": "<id or null>",
                "pass_through_entity": "<entity or null>",
                "notes": "<notes>"
            }
        ]
    }
    """

    pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")

    try:
        response = ai_client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[pdf_part, prompt]
        )
        res_text = response.text.replace('```json', '').replace('```', '').strip()
        parsed = json.loads(res_text)
        return parsed
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

def save_to_bigquery(finding):
    client = bigquery.Client(project=GCP_PROJECT)
    table_id = f"{GCP_PROJECT}.{BQ_DATASET}.mercy_house_schedule_i"

    schema = [
        bigquery.SchemaField("organization_name", "STRING"),
        bigquery.SchemaField("fiscal_year", "STRING"),
        bigquery.SchemaField("total_government_grants", "FLOAT64"),
        bigquery.SchemaField("misclassified_grant_amount", "FLOAT64"),
        bigquery.SchemaField("misclassification_notes", "STRING"),
        bigquery.SchemaField("grants_json", "STRING"),
        bigquery.SchemaField("extracted_at", "TIMESTAMP"),
    ]

    try:
        client.get_table(table_id)
    except Exception:
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)

    rows_to_insert = [{
        "organization_name": finding.get("organization_name"),
        "fiscal_year": finding.get("fiscal_year"),
        "total_government_grants": finding.get("total_government_grants"),
        "misclassified_grant_amount": finding.get("misclassified_grant_amount"),
        "misclassification_notes": finding.get("misclassification_notes"),
        "grants_json": json.dumps(finding.get("grants", [])),
        "extracted_at": "CURRENT_TIMESTAMP()",
    }]

    query = f"""
        INSERT INTO `{table_id}`
        (organization_name, fiscal_year, total_government_grants, misclassified_grant_amount,
         misclassification_notes, grants_json, extracted_at)
        VALUES
        (@org, @fy, @total, @misclass, @notes, @grants_json, CURRENT_TIMESTAMP())
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("org", "STRING", finding.get("organization_name")),
            bigquery.ScalarQueryParameter("fy", "STRING", finding.get("fiscal_year")),
            bigquery.ScalarQueryParameter("total", "FLOAT64", finding.get("total_government_grants")),
            bigquery.ScalarQueryParameter("misclass", "FLOAT64", finding.get("misclassified_grant_amount")),
            bigquery.ScalarQueryParameter("notes", "STRING", finding.get("misclassification_notes")),
            bigquery.ScalarQueryParameter("grants_json", "STRING", json.dumps(finding.get("grants", []))),
        ]
    )
    client.query(query, job_config=job_config).result()
    print("Saved Schedule I extraction to BigQuery.")

def main():
    if not os.path.exists(PDF_PATH):
        print(f"PDF not found: {PDF_PATH}")
        return

    finding = extract_schedule_i(PDF_PATH)
    if finding:
        print("\n=== MERCY HOUSE SCHEDULE I / FEDERAL AWARDS ===")
        print(json.dumps(finding, indent=2))
        print("===============================================\n")
        save_to_bigquery(finding)
    else:
        print("Failed to extract Schedule I.")

if __name__ == "__main__":
    main()
