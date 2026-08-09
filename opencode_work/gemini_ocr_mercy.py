import os
import google.auth as gar
import google.genai as genai
from google.genai import types

PROJECT = "noble-beanbag-497411-m4"
LOCATION = "us-central1"
OUTPUT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work"

creds, proj = gar.default()
client = genai.Client(vertexai=True, project=proj, location=LOCATION)

MODEL = "gemini-2.5-flash"

pdf_paths = [
    r"G:\BACKUP ASUS 24\DOCS2\2022-MERCY HOUSE LIVING CENTERS-Returns-06.30.23 PUBLIC.pdf",
    r"G:\619onedrivepost\backup tclphone\dls\Mercy House Living Centers - Full Filing - Nonprofit Explorer - ProPublica.pdf",
]

for pdf_path in pdf_paths:
    if not os.path.exists(pdf_path):
        print(f"NOT FOUND: {pdf_path}")
        continue

    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(pdf_path)}")
    print(f"{'='*60}")

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    print(f"PDF size: {len(pdf_data) / 1024:.1f} KB")

    prompt = """You are analyzing a nonprofit 990 tax return. Extract and return the following structured information:
1. Organization name and EIN
2. Gross receipts / total revenue
3. Total assets
4. Total liabilities
5. Grants and assistance amounts
6. Officer / director / trustee names and compensation
7. Any related party transactions
8. Revenue sources breakdown (contributions, program service revenue, etc.)
9. Expenses breakdown
10. Net assets / fund balance at beginning and end

Return the data in a structured format. If a section is not clearly identifiable, note it as 'Not found in document'."""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Part(inline_data=types.Blob(data=pdf_data, mime_type="application/pdf")),
                prompt,
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=1024)
            ),
        )
        text = response.text

        # Save output
        safe_name = os.path.basename(pdf_path).replace(".pdf", "").replace(" ", "_")
        out_path = os.path.join(OUTPUT_DIR, f"mercy_house_990_parsed_{safe_name}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"\nSaved: {out_path}")
        print(f"\nPreview:\n{text[:2000]}")
        print(f"\n... [truncated at 2000 chars] ...")

    except Exception as e:
        print(f"ERROR: {e}")

print("\nDone.")
