import fitz
import json
import os
from datetime import datetime

# Use the manifest from our workspace
manifest_path = r"C:\OsintNeoAi\workspaces\riconow\opencode_work\permit_backups_manifest.txt"
output_dir = r"C:\OsintNeoAi\workspaces\riconow\opencode_work\ocr_output_permits"
os.makedirs(output_dir, exist_ok=True)

with open(manifest_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

pdfs = [line.strip() for line in lines if line.strip().lower().endswith(".pdf")]
print(f"Total PDF files: {len(pdfs)}")

# Filter for HBNC/Cameron/StormTech related
keywords = ["17631", "17642", "cameron", "beach blvd", "stormtech", "storm", "hbnc", "huntington beach", "navigation center"]
target_pdfs = []
for pdf in pdfs:
    for kw in ["17631", "17642", "cameron", "stormtech"]:
        if kw.lower() in pdf.lower():
            target_pdfs.append(pdf)
            break

print(f"Target PDFs for OCR: {len(target_pdfs)}")
for p in target_pdfs:
    print(f"  {p}")

# Process target PDFs
results = []
for pdf_path in target_pdfs:
    if not os.path.exists(pdf_path):
        print(f"Missing: {pdf_path}")
        continue
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            text += page.get_text()
        doc.close()
        
        result = {
            "file_path": pdf_path,
            "file_name": os.path.basename(pdf_path),
            "page_count": len(doc) if 'doc' in locals() else 0,
            "extracted_text": text[:50000],
            "ocr_timestamp": datetime.utcnow().isoformat() + "Z"
        }
        results.append(result)
        
        # Save individual result
        out_name = os.path.basename(pdf_path).replace(".pdf", "_ocr.json")
        out_path = os.path.join(r"C:\OsintNeoAi\workspaces\riconow\opencode_work\ocr_output_permits", out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Processed: {os.path.basename(pdf_path)}")
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

# Save combined results
combined_path = os.path.join(r"C:\OsintNeoAi\workspaces\riconow\opencode_work\ocr_output_permits", "combined_results.json")
with open(combined_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"\nCombined results saved to: {combined_path}")
print(f"Total processed: {len(results)}")