import os
import sys
import glob
import json
import re

PHOTOS_DIR_1 = r"C:\OsintNeoAi\evidence\google_photos_evidence"
PHOTOS_DIR_2 = r"C:\OsintNeoAi\evidence\google_photos_evidence_batch2"
OUTPUT_DIR = r"C:\OsintNeoAi\evidence\ocr_transcripts_photos"
INDEX_FILE = r"C:\OsintNeoAi\evidence\PHOTOS_EVIDENCE_OCR_INDEX.md"

KEYWORDS = [
    "Unlawful Detainer", "UD", "ROA", "Register of Actions", "Case No", "30-202",
    "Superior Court", "Summons", "Proof of Service", "Due Diligence", "Default",
    "Writ", "Possession", "Andrew Do", "Cheri Pham", "Rhiannon Do", "Pham", "Do",
    "Viet America", "VAS", "17642 Beach", "7942 Speer", "Warner", "Hardy", "Huntington Beach",
    "Sheriff", "Eviction", "Defendant", "Plaintiff"
]

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    print("✓ RapidOCR initialized for Photo Album Scanning.")

    all_photos = []
    for d in [PHOTOS_DIR_1, PHOTOS_DIR_2]:
        if os.path.exists(d):
            for ext in ["*.jpg", "*.jpeg", "*.png"]:
                all_photos.extend(glob.glob(os.path.join(d, ext)))

    print(f"Total photos to OCR: {len(all_photos)}")
    
    hits = []
    
    for idx, photo_path in enumerate(all_photos):
        filename = os.path.basename(photo_path)
        folder = os.path.basename(os.path.dirname(photo_path))
        print(f"[{idx+1}/{len(all_photos)}] Scanning {folder}/{filename}...")
        
        try:
            res, _ = ocr(photo_path)
            extracted_text = ""
            if res:
                extracted_text = "\n".join([line[1] for line in res])
            else:
                extracted_text = "[NO TEXT DETECTED]"
        except Exception as e:
            extracted_text = f"[OCR ERROR: {e}]"

        # Save transcript
        out_txt = os.path.join(OUTPUT_DIR, f"{folder}_{filename}.txt")
        with open(out_txt, "w", encoding="utf-8", errors="ignore") as f:
            f.write(extracted_text)

        matched_kws = []
        for kw in KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', extracted_text, re.IGNORECASE):
                matched_kws.append(kw)

        if matched_kws or len(extracted_text) > 100:
            hits.append({
                "folder": folder,
                "filename": filename,
                "matched_kws": matched_kws,
                "snippet": extracted_text[:350].replace("\n", " "),
                "full_text": extracted_text
            })
            print(f"    ⭐ HIT! Matched: {matched_kws} | Text len: {len(extracted_text)}")

    # Generate Summary Markdown
    lines = [
        "# GOOGLE PHOTOS OCR & EVIDENCE REPORT",
        f"**Scanned Photos:** {len(all_photos)} images",
        f"**Significant Hits:** {len(hits)} photos with readable legal/property text",
        "",
        "---",
        "",
        "## Top Legal & Case Hits:",
        ""
    ]

    for h in hits:
        lines.append(f"### 📷 `{h['folder']}/{h['filename']}`")
        lines.append(f"* **Keywords:** {', '.join(h['matched_kws']) if h['matched_kws'] else 'Dense Text Record'}")
        lines.append(f"* **OCR Transcript:** > *{h['snippet']}*\n")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n[✓] Finished Photo OCR! Report written to: {INDEX_FILE}")

if __name__ == "__main__":
    main()
