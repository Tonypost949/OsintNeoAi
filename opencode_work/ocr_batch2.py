"""Batch 2: Large PDFs (page-by-page) including missing forensic files"""
import os, re, time
import fitz
import google.auth
import google.genai as genai
from google.genai import types as gtypes

OUT = r"C:\Users\HP\OneDrive\Documents\opencode_work\ocr_output"

# Find missing/large files with corrected paths
LARGE_FILES = []

# Search for files by key terms
search_dirs = [r"G:\DL BACKUP", r"G:\buckp moto\Download"]
search_terms = ["forensic investigation report", "andrew-do-forensic", "future development 17642", 
                "HBNC", "navigation center contamination", "17631 Cameron Ln",
                "forensic well", "GPR field use well", "grid scale", "HB_IRC_Report",
                "dimarcello", "site assessment report 17631", "site assessment report additonal",
                "Huntington Beach City Clerks", "SB-1928", "military equipment",
                "Shea Parkside", "chris plea", "aebhw25"]

for d in search_dirs:
    if not os.path.isdir(d):
        continue
    for root, dirs_, files in os.walk(d):
        for f in files:
            if not f.lower().endswith('.pdf'):
                continue
            fp = os.path.join(root, f)
            fname_lower = f.lower()
            matched = False
            for term in search_terms:
                if term.lower() in fname_lower:
                    matched = True
                    break
            if not matched:
                continue
            
            size_mb = os.path.getsize(fp) / 1e6
            # Skip tiny files and already-processed duplicates
            if size_mb < 0.05:
                continue
            
            safe = re.sub(r'[^\w\-\.]', '_', os.path.basename(fp))[:50]
            out_txt = os.path.join(OUT, f"ocr_{safe}.txt")
            if os.path.exists(out_txt) and os.path.getsize(out_txt) > 200:
                print(f"[CACHED] {os.path.basename(fp)[:60]} ({size_mb:.1f}MB)")
                continue
            
            LARGE_FILES.append((fp, size_mb))

# Deduplicate
seen = set()
unique = []
for fp, sz in LARGE_FILES:
    key = os.path.basename(fp).lower()
    if key not in seen:
        seen.add(key)
        unique.append((fp, sz))

LARGE_FILES = unique
print(f"Found {len(LARGE_FILES)} large PDFs to process\n")

# Also add the exact SITE ASSESSMENT REPORT files
extra = [
    r"G:\DL BACKUP\SITE ASSESSMENT REPORT  - SITE ASSESSMENT REPORT - Site Assessment Report - 17631 Cameron Ln - 18330.0006.00.pdf",
    r"G:\DL BACKUP\SITE ASSESSMENT REPORT  - SITE ASSESSMENT REPORT - Additonal Assessment Report 17642 Beach Blvd - 18334.0004.00.pdf",
]
for ep in extra:
    if os.path.exists(ep):
        safe = re.sub(r'[^\w\-\.]', '_', os.path.basename(ep))[:50]
        out_txt = os.path.join(OUT, f"ocr_{safe}.txt")
        if not (os.path.exists(out_txt) and os.path.getsize(out_txt) > 200):
            LARGE_FILES.append((ep, os.path.getsize(ep) / 1e6))

FLAG_PATTERNS = [
    (r"ONNI", "ONNI"),
    (r"G\s*&?\s*M\s*Oil", "G&M Oil"),
    (r"17642", "17642"),
    (r"17472", "17472"),
    (r"Cameron", "Cameron"),
    (r"Yamada", "Yamada"),
    (r"Mitsuru", "Mitsuru"),
    (r"cesspool", "cesspool"),
    (r"contaminat", "contamination"),
    (r"varianc", "variance"),
    (r"waiver", "waiver"),
    (r"HBNC", "HBNC"),
    (r"navigation.center", "nav center"),
    (r"homeless.shelter", "homeless shelter"),
    (r"APN", "APN"),
    (r"well", "well"),
    (r"irrigation", "irrigation"),
    (r"demolition", "demolition"),
    (r"UST", "UST"),
    (r"GeoTracker", "GeoTracker"),
    (r"benzene", "benzene"),
    (r"MTBE", "MTBE"),
    (r"RWQCB", "RWQCB"),
    (r"DTSC", "DTSC"),
    (r"Environmental FRAUD", "env fraud"),
]

def scan_flags(text):
    found = {}
    for pattern, label in FLAG_PATTERNS:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found[label] = list(set(matches))[:3]
        except:
            pass
    return found

print("Connecting to Vertex AI...")
creds, proj = google.auth.default()
client = genai.Client(vertexai=True, project=proj, location="us-central1")
print(f"Project: {proj}\n")

stats = {"ok": 0, "err": 0, "pages": 0}

for fpath, size_mb in LARGE_FILES:
    fname = os.path.basename(fpath)
    safe = re.sub(r'[^\w\-\.]', '_', fname)[:50]
    out_txt = os.path.join(OUT, f"ocr_{safe}.txt")
    
    # Skip already processed
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 200:
        text = open(out_txt, encoding="utf-8", errors="replace").read()
        flags = scan_flags(text)
        print(f"[CACHED] {fname[:60]} ({size_mb:.1f}MB, {len(flags)} flag categories)")
        continue
    
    print(f"\n[{fname[:60]}] {size_mb:.1f}MB ...", flush=True)
    
    try:
        doc = fitz.open(fpath)
        total_pages = len(doc)
        max_pages = min(total_pages, 30)  # Cap at 30 pages for speed
        print(f"  {max_pages} of {total_pages} pages...", flush=True)
        
        all_text = []
        for pn in range(max_pages):
            try:
                pix = doc[pn].get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                prompt = f"OCR this page {pn+1} of {fname}. Extract ALL text verbatim. Note any: ONNI, G&M Oil, 17472, 17642, Cameron, Yamada, APN, well, UST, variance, waiver, HBNC, navigation center, environmental violation, permit number."
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        gtypes.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                        prompt,
                    ],
                )
                all_text.append(f"--- PAGE {pn+1} ---\n{resp.text}")
                stats["pages"] += 1
            except Exception as pe:
                all_text.append(f"--- PAGE {pn+1} ERROR: {pe} ---")
            
            if (pn + 1) % 5 == 0:
                print(f"  Page {pn+1}/{max_pages}", flush=True)
                time.sleep(3)
            elif (pn + 1) % 3 == 0:
                time.sleep(1)
        
        doc.close()
        text = "\n".join(all_text)
        
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(text)
        
        flags = scan_flags(text)
        print(f"  [OK] {len(text)} chars")
        if flags:
            for label, vals in sorted(flags.items()):
                print(f"    [{label}]: {', '.join(vals[:2])}")
        stats["ok"] += 1
        
    except Exception as e:
        print(f"  [ERR] {str(e)[:120]}")
        stats["err"] += 1
    
    time.sleep(3)

print(f"\nDONE: {stats['ok']} ok, {stats['err']} err, {stats['pages']} pages processed")
