import os
import sys
import glob
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

BATCHES = [
    r"C:\OsintNeoAi\evidence\google_photos_evidence",
    r"C:\OsintNeoAi\evidence\google_photos_evidence_batch2",
    r"C:\OsintNeoAi\evidence\google_photos_evidence_batch3"
]

OUTPUT_DIR = r"C:\OsintNeoAi\evidence\ocr_transcripts_photos"
INDEX_FILE = r"C:\OsintNeoAi\evidence\PHOTOS_EVIDENCE_OCR_INDEX.md"

KEYWORDS = [
    "Unlawful Detainer", "UD", "ROA", "Register of Actions", "Case No", "30-202",
    "Superior Court", "Summons", "Proof of Service", "Due Diligence", "Default",
    "Writ", "Possession", "Andrew Do", "Cheri Pham", "Rhiannon Do", "Pham", "Do",
    "Viet America", "VAS", "17642 Beach", "7942 Speer", "Warner", "Hardy", "Huntington Beach",
    "Sheriff", "Eviction", "Defendant", "Plaintiff", "Ewing", "Chain of Custody"
]

def process_photo(photo_path, ocr_engine):
    filename = os.path.basename(photo_path)
    folder = os.path.basename(os.path.dirname(photo_path))
    out_txt = os.path.join(OUTPUT_DIR, f"{folder}_{filename}.txt")
    
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 0:
        with open(out_txt, "r", encoding="utf-8", errors="ignore") as fp:
            extracted_text = fp.read()
    else:
        try:
            res, _ = ocr_engine(photo_path)
            if res:
                extracted_text = "\n".join([line[1] for line in res])
            else:
                extracted_text = "[NO TEXT DETECTED]"
        except Exception as e:
            extracted_text = f"[OCR ERROR: {e}]"
            
        with open(out_txt, "w", encoding="utf-8", errors="ignore") as out_f:
            out_f.write(extracted_text)

    matched_kws = []
    for kw in KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', extracted_text, re.IGNORECASE):
            matched_kws.append(kw)

    return {
        "folder": folder,
        "filename": filename,
        "text_len": len(extracted_text),
        "matched_kws": matched_kws,
        "snippet": extracted_text[:350].replace("\n", " "),
        "full_text": extracted_text
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()

    all_photos = []
    for d in BATCHES:
        if os.path.exists(d):
            for ext in ["*.jpg", "*.jpeg", "*.png"]:
                all_photos.extend(glob.glob(os.path.join(d, ext)))

    print(f"=== Starting High-Speed Neural OCR on {len(all_photos)} Photos ===")
    
    results = []
    # Process sequentially with fast ONNX runtime
    for i, p in enumerate(all_photos):
        res = process_photo(p, ocr)
        results.append(res)
        if res["matched_kws"] or res["text_len"] > 120:
            print(f"[{i+1}/{len(all_photos)}] ⭐ HIT in {res['folder']}/{res['filename']} -> Matched: {res['matched_kws']}")
        elif (i+1) % 25 == 0:
            print(f"[{i+1}/{len(all_photos)}] Processed...")

    # Write Master Markdown Report
    hits = [r for r in results if r["matched_kws"] or r["text_len"] > 100]
    
    lines = [
        "# MASTER GOOGLE PHOTOS EVIDENCE & COURT AUDIT REPORT",
        f"**Total Photos Processed:** {len(all_photos)} images across 3 albums",
        f"**High-Confidence Text Documents:** {len(hits)} evidentiary records",
        "",
        "---",
        "",
        "## 1. Forensic Keyword Matrix",
        ""
    ]

    kw_summary = {}
    for kw in KEYWORDS:
        m = [r for r in results if kw in r["matched_kws"]]
        if m:
            kw_summary[kw] = len(m)
            lines.append(f"* **{kw}:** {len(m)} matching photos")

    lines.append("\n---\n\n## 2. Granular Document Findings\n")
    for h in hits:
        lines.append(f"### 📷 `{h['folder']}/{h['filename']}`")
        if h['matched_kws']:
            lines.append(f"* **Keywords Detected:** `{', '.join(h['matched_kws'])}`")
        lines.append(f"* **Transcript Snippet:** > *{h['snippet']}*\n")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n[✓] All {len(all_photos)} photos processed! Report saved to {INDEX_FILE}")

if __name__ == "__main__":
    main()
