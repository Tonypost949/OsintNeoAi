import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', '')
PDF_PATH = r"G:\DL BACKUP\non profit data mercy house 2024-06-GSAFAC-0000355035.pdf"

import google.generativeai as genai
if os.environ['GOOGLE_API_KEY']:
    genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

with open(PDF_PATH, 'rb') as f:
    pdf_bytes = f.read()
print(f"PDF size: {len(pdf_bytes):,} bytes")

prompt = """You are a forensic auditor. Extract from this Form 990 these exact figures:
1. Fiscal Year End
2. Total Revenue (Part I, Line 12 or Part VIII)
3. Total Expenses (Part I, Line 18 or Part IX)
4. Net Assets (Part I, Line 22 or Part X)
5. Total federal grant funding received
6. Executive compensation (Part VII-A)

Return ONLY JSON:
{"fiscal_year": "<year>", "total_revenue": <number>, "total_expenses": <number>, "net_assets": <number>, "grant_funding": <number>, "executive_compensation": <number>, "assessment": "<summary>"}"""

print("Uploading to Gemini...")
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content([{"mime_type": "application/pdf", "data": pdf_bytes}, prompt])

res_text = response.text.strip()
print(f"\nResponse ({len(res_text)} chars):")
print(res_text[:1500])

# Parse JSON
try:
    result = json.loads(res_text)
except:
    for marker in ["```json", "```"]:
        if marker in res_text:
            parts = res_text.split(marker)
            for p in parts:
                p = p.strip().strip("`").strip()
                if p.startswith("{"):
                    result = json.loads(p)
                    break
            break
    else:
        start = res_text.find("{")
        end = res_text.rfind("}") + 1
        result = json.loads(res_text[start:end])

result["organization_name"] = "Mercy House Living Centers"
print("\n=== RESULT ===")
print(json.dumps(result, indent=2))

out_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\mercy_house_990_gemini.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
print(f"\nSaved to {out_path}")
