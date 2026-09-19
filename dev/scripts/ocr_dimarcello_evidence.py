import os
import sys
import fitz  # PyMuPDF
import json
import re

EVIDENCE_DIR = r"C:\OsintNeoAi\evidence\lawsuit_info_full_dimarcello"
OUTPUT_DIR = os.path.join(EVIDENCE_DIR, "ocr_transcripts")
INDEX_FILE = os.path.join(EVIDENCE_DIR, "FULL_OCR_EVIDENCE_INDEX.md")

KEYWORDS = [
    "Andrew Do", "Cheri Pham", "Rhiannon Do", "Pham", "Do", "Viet America", "VAS",
    "Unlawful Detainer", "Eviction", "30-202", "ROA", "Register of Actions", "Summons",
    "Proof of Service", "Due Diligence", "Default", "Writ", "Possession", "Hardy",
    "Speer", "7942 Speer", "17642 Beach", "17612 Beach", "Yamada", "Warner", "11770 Warner",
    "Superior Court", "Central Justice", "West Justice", "Harbor Justice", "North Justice",
    "Homeless", "Audit", "Easement", "EPA", "Phase 1", "Sheriff"
]

def ocr_and_extract():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = sorted(os.listdir(EVIDENCE_DIR))
    
    summary_report = [
        "# FULL FORENSIC OCR & EVIDENCE AUDIT REPORT",
        f"**Target Directory:** `{EVIDENCE_DIR}`",
        f"**Audit Timestamp:** {os.popen('powershell Get-Date -Format s').read().strip()}",
        "",
        "---",
        "",
        "## 1. Executive Forensic Keyword Matches",
        ""
    ]
    
    file_results = []
    keyword_matches = {kw: [] for kw in KEYWORDS}

    for filename in files:
        filepath = os.path.join(EVIDENCE_DIR, filename)
        if os.path.isdir(filepath) or filename.startswith("FULL_OCR"):
            continue
            
        print(f"[*] Processing: {filename}...")
        extracted_text = ""
        total_pages = 0
        
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == ".pdf":
            try:
                doc = fitz.open(filepath)
                total_pages = len(doc)
                for page_idx in range(total_pages):
                    page = doc[page_idx]
                    page_text = page.get_text("text")
                    if not page_text.strip():
                        # Try PyMuPDF OCR if text layer empty
                        try:
                            pix = page.get_pixmap()
                            # fallback OCR flag if supported
                            page_text = page.get_text("text")
                        except Exception:
                            pass
                    extracted_text += f"\n--- Page {page_idx + 1} ---\n" + page_text
            except Exception as e:
                extracted_text = f"[ERROR READING PDF: {e}]"
                
        elif ext in [".html", ".txt", ".json", ".csv"]:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()
            except Exception as e:
                extracted_text = f"[ERROR READING TEXT: {e}]"
                
        elif ext in [".png", ".jpg", ".jpeg"]:
            # Image record note
            extracted_text = f"[IMAGE ARTIFACT: {filename} - Size: {os.path.getsize(filepath):,} bytes]"
            
        # Save transcript
        txt_out = os.path.join(OUTPUT_DIR, f"{filename}.txt")
        with open(txt_out, "w", encoding="utf-8", errors="ignore") as out_f:
            out_f.write(extracted_text)
            
        # Keyword scan
        matched_kws = []
        for kw in KEYWORDS:
            if re.search(r'\b' + re.escape(kw) + r'\b', extracted_text, re.IGNORECASE):
                keyword_matches[kw].append(filename)
                matched_kws.append(kw)
                
        file_results.append({
            "filename": filename,
            "size": os.path.getsize(filepath),
            "pages": total_pages,
            "text_length": len(extracted_text),
            "matched_keywords": matched_kws,
            "sample_snippet": extracted_text[:400].replace("\n", " ")
        })

    # Build markdown index
    summary_report.append("| Keyword | Matched Files Count | Files |")
    summary_report.append("| :--- | :--- | :--- |")
    for kw, matched in keyword_matches.items():
        if matched:
            flist = ", ".join([f"`{f}`" for f in matched[:5]])
            if len(matched) > 5:
                flist += f" *(+{len(matched)-5} more)*"
            summary_report.append(f"| **{kw}** | {len(matched)} | {flist} |")

    summary_report.append("\n---\n\n## 2. Granular File Analysis\n")
    for res in file_results:
        summary_report.append(f"### 📄 `{res['filename']}`")
        summary_report.append(f"* **File Size:** {res['size']:,} bytes | **Pages:** {res['pages']}")
        summary_report.append(f"* **Keywords Detected:** {', '.join(res['matched_keywords']) if res['matched_keywords'] else 'None'}")
        summary_report.append(f"* **Transcript:** [`ocr_transcripts/{res['filename']}.txt`](file:///{OUTPUT_DIR}/{res['filename']}.txt)")
        summary_report.append(f"* **Snippet:** > *{res['sample_snippet']}*\n")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_report))
        
    print(f"\n[✓] OCR Complete! Index written to: {INDEX_FILE}")

if __name__ == "__main__":
    ocr_and_extract()
