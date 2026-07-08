import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

import vertexai
from vertexai.generative_models import GenerativeModel, Part

vertexai.init(
    project="noble-beanbag-497411-m4",
    location="us-central1"
)

PDF_PATH = r"G:\DL BACKUP\non profit data mercy house 2024-06-GSAFAC-0000355035.pdf"

def main():
    if not os.path.exists(PDF_PATH):
        print(f"PDF not found: {PDF_PATH}")
        return

    print(f"Reading PDF: {PDF_PATH}")
    with open(PDF_PATH, 'rb') as f:
        pdf_bytes = f.read()
    print(f"PDF size: {len(pdf_bytes):,} bytes")

    print("Creating PDF Part...")
    pdf_part = Part.from_data(data=pdf_bytes, mime_type="application/pdf")

    prompt = """You are OSINTNeoAi, a forensic data auditor. Below is a Form 990 public tax return PDF for Mercy House Living Centers.
Extract and return ONLY a JSON block with these exact metrics:
1. Fiscal Year End / Tax Year
2. Total Revenue (Form 990 Part I, Line 12 or Part VIII)
3. Total Expenses (Form 990 Part I, Line 18 or Part IX)
4. Net Assets / Fund Balances (Form 990 Part I, Line 22 or Part X)
5. Total Grants government funding received (Part IX)
6. Executive compensation (Part VII-A)
7. Any fund flow discrepancies or unexplained outflows

Return ONLY valid JSON (no markdown, no backticks):
{
    "organization_name": "Mercy House Living Centers",
    "fiscal_year": "<year>",
    "total_revenue": <float or null>,
    "total_expenses": <float or null>,
    "net_assets": <float or null>,
    "executive_compensation": <float or null>,
    "grant_funding": <float or null>,
    "unaccounted_fund_delta": <float or null>,
    "assessment": "<findings summary with exact figures>"
}"""

    try:
        model = GenerativeModel("gemini-2.0-flash")
        print("Sending to Vertex AI Gemini...")
        response = model.generate_content([pdf_part, prompt])
        res_text = response.text.strip()

        print(f"\nRaw response (first 800 chars):\n{res_text[:800]}")

        try:
            result = json.loads(res_text)
        except json.JSONDecodeError:
            for marker in ["```json", "```JSON", "```"]:
                if marker in res_text:
                    parts = res_text.split(marker)
                    for p in parts:
                        stripped = p.strip().strip("`").strip()
                        if stripped.startswith("{"):
                            result = json.loads(stripped)
                            break
                    break
            else:
                start = res_text.find("{")
                end = res_text.rfind("}") + 1
                if start != -1 and end != 0:
                    result = json.loads(res_text[start:end])
                else:
                    raise ValueError("Could not find JSON in response")

        print("\n--- MERCY HOUSE 990 FORENSIC ANALYSIS ---")
        print(json.dumps(result, indent=2))
        print("------------------------------------------\n")

        output_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\mercy_house_990_analysis.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"Saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()