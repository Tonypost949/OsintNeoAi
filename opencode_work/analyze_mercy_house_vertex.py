import os
import google.auth
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import pypdf

creds, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
vertexai.init(project=project, credentials=creds, location="us-central1")

model = GenerativeModel("gemini-1.5-flash")

pdf_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7\2022-MERCY_HOUSE_PUBLIC_RETURN.pdf"
output_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work"

print("Extracting text from PDF...")
reader = pypdf.PdfReader(pdf_path)
print(f"Pages: {len(reader.pages)}")

all_text = ""
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text and text.strip():
        all_text += f"\n--- PAGE {i+1} ---\n{text}"
    if i % 5 == 0:
        print(f"  Extracted page {i+1}/{len(reader.pages)}")

print(f"\nTotal text extracted: {len(all_text)} chars")

if len(all_text.strip()) < 100:
    print("ERROR: PDF appears to be scanned - pypdf extracted minimal text")
    print("Trying image-based extraction...")
    
    prompt = """You are analyzing a 990 tax form for Mercy House Community Development Corporation.
    Extract ALL financial data, officer names, board member names, grant recipients, 
    revenue figures, expenses, compensation amounts, and any RICO-relevant information.
    Format as structured markdown with sections."""
    
    from PIL import Image
    import io
    
    for i, page in enumerate(reader.pages):
        print(f"  Processing page {i+1}/{len(reader.pages)} as image...")
        page_image_path = os.path.join(output_dir, f"mercy_house_page_{i+1}.png")
        
        print(f"Would save page {i+1} to {page_image_path}")
    
    print("Image-based extraction would require tesseract or cloud vision API")
else:
    print("\nSending to Gemini for analysis...")
    
    prompt = """You are analyzing a 990 tax form for Mercy House Community Development Corporation.
    Extract and organize:
    1. **Organization Info**: Name, EIN, Address, Year
    2. **Revenue**: Total revenue, contributions/gifts, program service revenue
    3. **Expenses**: Total expenses, grants to other organizations, compensation
    4. **Officers/Key Employees**: Names and compensation
    5. **Board Members**: Names
    6. **Grant Recipients**: Any organizations receiving grants
    7. **Related Parties**: Any RICO-relevant transactions or relationships
    8. **Functional Expenses**: Breakdown by category
    
    Format as structured markdown."""

    max_chars = 150000
    if len(all_text) > max_chars:
        all_text = all_text[:max_chars] + "\n\n[TRUNCATED]"

    response = model.generate_content([
        Part.from_text(prompt),
        Part.from_text(all_text)
    ])
    
    print("\n=== MERCY HOUSE 990 ANALYSIS ===")
    print(response.text)
    
    report_path = os.path.join(output_dir, "mercy_house_990_analysis.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"\nSaved to: {report_path}")
