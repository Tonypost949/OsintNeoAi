import os
import glob
import re
from rapidocr_onnxruntime import RapidOCR

BATCH_DIR = r"C:\OsintNeoAi\evidence\google_photos_evidence_batch8"
OUT_DIR = r"C:\OsintNeoAi\evidence\ocr_transcripts_photos"
INDEX_FILE = r"C:\OsintNeoAi\evidence\BATCH8_OCR_INDEX.md"

KEYWORDS = [
    "Hamilton", "Police", "Innocenzi", "Dean Innocenzi", "2019-00053723", "2020-00008897",
    "Quantum", "Auto Dismantler", "Santa Ana", "3125 W 5th", "Cedar Lane", "1456 Cedar",
    "Dog's Day Productions", "Greenacres", "Florida", "SS-4", "Alaska", "Flight 1129",
    "Philadelphia", "Los Angeles", "LAX", "PHL", "Summons", "Complaint", "2020-613", "1103-2019-002671"
]

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ocr = RapidOCR()
    photos = sorted(glob.glob(os.path.join(BATCH_DIR, "*.jpg")))
    print(f"=== Starting Batch 8 Complete OCR across {len(photos)} photos ===")

    hits = []
    for idx, p in enumerate(photos):
        fn = os.path.basename(p)
        txt_file = os.path.join(OUT_DIR, f"batch8_{fn}.txt")

        # Skip if already OCR'd and not empty
        if os.path.exists(txt_file) and os.path.getsize(txt_file) > 10:
            with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read()
        else:
            try:
                res, _ = ocr(p)
                if res:
                    extracted_text = "\n".join([line[1] for line in res])
                else:
                    extracted_text = "[NO TEXT DETECTED]"
            except Exception as e:
                extracted_text = f"[OCR ERROR: {e}]"

            with open(txt_file, "w", encoding="utf-8", errors="ignore") as f:
                f.write(extracted_text)

        matched_kws = []
        for kw in KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', extracted_text, re.IGNORECASE):
                matched_kws.append(kw)

        if matched_kws or len(extracted_text) > 120:
            hits.append({
                "filename": fn,
                "matched_kws": matched_kws,
                "snippet": extracted_text[:300].replace("\n", " "),
                "full_text": extracted_text
            })
            print(f"[{idx+1}/{len(photos)}] ⭐ HIT! {fn} -> {matched_kws} ({len(extracted_text)} chars)")
        elif (idx + 1) % 25 == 0:
            print(f"[{idx+1}/{len(photos)}] Processed...")

    lines = [
        "# BATCH 8 FORENSIC OCR REPORT",
        f"**Total Photos in Batch:** {len(photos)}",
        f"**Document Hits:** {len(hits)}",
        "",
        "---",
        ""
    ]

    for h in hits:
        lines.append(f"### 📷 `{h['filename']}`")
        if h['matched_kws']:
            lines.append(f"* **Matched Keywords:** `{', '.join(h['matched_kws'])}`")
        lines.append(f"* **Transcript:** > *{h['snippet']}*\n")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n[✓] Batch 8 OCR Complete! Report written to {INDEX_FILE}")

if __name__ == "__main__":
    main()
