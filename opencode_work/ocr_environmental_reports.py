import os
import google.auth as gar
import google.genai as genai
from google.genai import types
import time

OUTPUT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work"
creds, proj = gar.default()
client = genai.Client(vertexai=True, project=proj, location="us-central1")
MODEL = "gemini-2.5-flash"

files = [
    (
        r"G:\buckp moto\Download\Forensic Investigation Report- Environmental Fraud and Hydrogeological Hazards at 17642 Beach Blvd, Huntington Beach.pdf",
        "forensic_17642_beach.txt",
        "Extract: (1) site address/APN, (2) contaminants found and levels, (3) hydrogeological hazards, (4) responsible parties named, (5) regulatory violations, (6) financial damages, (7) connection to homelessness shelter or government contracts"
    ),
    (
        r"G:\buckp moto\Download\Environmental Site Assessment Huntington Beach.pdf",
        "env_site_assessment.txt",
        "Extract: (1) site address and APN, (2) contaminants and levels, (3) regulatory status, (4) cleanup requirements, (5) property owner/responsible party, (6) historical use"
    ),
    (
        r"G:\DL BACKUP\T10000018579_2026-Jun-02-112324\HISTORIC FILES - PHASE I ENVIRONMENTAL SITE ASSESSMENT - T10000018579.20200318.Phase I Environmental Site Assessment.pdf",
        "phase1_esa.txt",
        "Extract: (1) site address/APN, (2) contaminants found, (3) regulatory status, (4) property owner, (5) historical use, (6) recommended actions"
    ),
    (
        r"G:\DL BACKUP\T10000018579_2026-Jun-02-112324\HISTORIC FILES - SITE ASSESSMENT REPORT - T10000018579.20200625.Site Assessment Report.pdf",
        "site_assessment_report.txt",
        "Extract: (1) site address/APN, (2) contaminants and levels, (3) regulatory citations, (4) responsible parties, (5) cleanup/remediation requirements"
    ),
]

for fpath, outname, prompt in files:
    if not os.path.exists(fpath):
        print(f"NOT FOUND: {fpath}")
        continue

    fname = os.path.basename(fpath)
    print(f"\n{'='*60}")
    print(f"Processing: {fname}")
    print(f"{'='*60}")

    try:
        with open(fpath, "rb") as f:
            pdf_data = f.read()

        print(f"PDF size: {len(pdf_data)/1024:.1f} KB")

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=MODEL,
                    contents=[
                        types.Part(inline_data=types.Blob(data=pdf_data, mime_type="application/pdf")),
                        prompt,
                    ],
                )
                text = response.text
                break
            except Exception as e:
                if attempt < 2:
                    print(f"Retry {attempt+2}...")
                    time.sleep(5)
                else:
                    raise

        out_path = os.path.join(OUTPUT_DIR, outname)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Saved: {out_path} ({len(text)} chars)")
        print(f"Preview:\n{text[:600]}\n...")

    except Exception as e:
        print(f"ERROR: {e}")

print("\nAll done.")
