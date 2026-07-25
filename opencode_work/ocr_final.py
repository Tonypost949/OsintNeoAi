"""Lightweight OCR: 2-3 pages from key remaining PDFs to avoid socket errors"""
import os, re, time
import fitz
import google.auth
import google.genai as genai
from google.genai import types as gtypes

OUT = r"C:\Users\HP\OneDrive\Documents\opencode_work\ocr_output"

TARGETS = [
    (r"G:\buckp moto\Download\andrew-do-forensic-audit-report-commissioned-by-county-phase-1.pdf", "Andrew Do Forensic Audit Phase 1"),
    (r"G:\buckp moto\Download\Future Development of 17642 Beach Blvd. - NO ACTION TAKEN (2).pdf", "17642 Future Development - No Action Taken"),
    (r"G:\buckp moto\Download\HB_IRC_Report_v1.1.pdf", "HB IRC Report v1.1"),
    (r"G:\DL BACKUP\T10000018579_2026-Jun-02-112324\SITE ASSESSMENT REPORT  - SITE ASSESSMENT REPORT - Additonal Assessment Report 17642 Beach Boulevard (003).pdf", "17642 Beach Additional Assessment"),
]

print("Init Gemini AI Studio Client (bypassing Vertex AI quota/permissions)...")
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set!")
client = genai.Client(api_key=api_key)

for fpath, desc in TARGETS:
    if not os.path.exists(fpath):
        print(f"\n[MISSING] {desc}")
        continue
    
    fname = os.path.basename(fpath)
    safe = re.sub(r'[^\w\-\.]', '_', fname)[:50]
    out_txt = os.path.join(OUT, f"ocr_{safe}.txt")
    
    is_failed = False
    if os.path.exists(out_txt):
        try:
            with open(out_txt, "r", encoding="utf-8", errors="ignore") as tf:
                content_sample = tf.read(2000)
                if "PERMISSION_DENIED" in content_sample or "Permission 'aiplatform.endpoints.predict' denied" in content_sample:
                    is_failed = True
        except Exception:
            pass
            
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 500 and not is_failed:
        print(f"\n[CACHED] {desc}")
        continue
    
    size_mb = os.path.getsize(fpath) / 1e6
    print(f"\n[{desc}] {size_mb:.1f}MB")
    
    try:
        doc = fitz.open(fpath)
        pages = len(doc)
        max_pg = min(pages, 5)  # Only first 5 pages
        print(f"  Pages: {pages} total, processing first {max_pg}...")
        
        all_text = []
        for pn in range(max_pg):
            try:
                pix = doc[pn].get_pixmap(dpi=150)
                img = pix.tobytes("png")
                prompt = f"OCR page {pn+1} of: {fname}. Extract ALL text verbatim."
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[gtypes.Part.from_bytes(data=img, mime_type="image/png"), prompt],
                )
                all_text.append(f"--- PAGE {pn+1} ---\n{resp.text}")
                print(f"  Page {pn+1} done")
            except Exception as pe:
                all_text.append(f"--- PAGE {pn+1} ERROR ---\n{pe}")
            time.sleep(3)
        
        doc.close()
        text = "\n".join(all_text)
        
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  Saved: {len(text)} chars")
        
    except Exception as e:
        print(f"  [ERR] {str(e)[:150]}")
    
    time.sleep(3)

print("\nDONE")
