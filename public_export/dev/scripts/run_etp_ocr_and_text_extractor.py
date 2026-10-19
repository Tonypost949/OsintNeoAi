import os
import glob
import json
import time
import re

BASE_DIR = r"C:\OsintNeoAi\data\takeouts\etp949609_takeout_20260913"
OCR_OUTPUT_DIR = os.path.join(BASE_DIR, "OCR_Extracted_Text")
DATA_DIR = os.path.join(BASE_DIR, "data")
METAMEDIA_DIR = os.path.join(BASE_DIR, "metamedia")
TAKEOUT_DIR = os.path.join(BASE_DIR, "Takeout")

os.makedirs(OCR_OUTPUT_DIR, exist_ok=True)

def run_deep_text_and_ocr_extraction():
    print(f"==================================================")
    print(f"DEEP OCR & TEXT EXTRACTION PIPELINE: ETP949609")
    print(f"Output Directory: {OCR_OUTPUT_DIR}")
    print(f"==================================================")

    # 1. Try PyMuPDF (fitz) for PDF documents
    try:
        import fitz
        has_fitz = True
    except ImportError:
        has_fitz = False

    extracted_records = []
    
    # Target all files across data/, metamedia/, Takeout/
    search_dirs = [DATA_DIR, METAMEDIA_DIR, TAKEOUT_DIR]
    all_target_files = []
    for sd in search_dirs:
        if os.path.exists(sd):
            for root, dirs, files in os.walk(sd):
                for f in files:
                    all_target_files.append(os.path.join(root, f))

    print(f"[EXTRACTOR] Found {len(all_target_files)} files to scan for text and OCR data...")

    text_extracted_count = 0

    for fpath in all_target_files:
        fname = os.path.basename(fpath)
        lower = fname.lower()
        
        extracted_text = ""
        source_type = "UNKNOWN"

        # A. PDFs
        if lower.endswith(".pdf") and has_fitz:
            try:
                doc = fitz.open(fpath)
                pages_text = []
                for pno in range(len(doc)):
                    pages_text.append(f"--- PAGE {pno+1} ---\n" + doc[pno].get_text())
                extracted_text = "\n".join(pages_text)
                source_type = "PDF_DOCUMENT"
            except Exception as e:
                pass

        # B. HTML / Bookmarks / Web Exports / Transcripts
        elif lower.endswith(".html") or lower.endswith(".htm"):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                    raw_html = fp.read()
                    # Strip tags for clean text transcript
                    clean_text = re.sub(r'<[^>]+>', ' ', raw_html)
                    extracted_text = ' '.join(clean_text.split())
                    source_type = "HTML_WEB_EXPORT"
            except Exception:
                pass

        # C. JSON Documents (Keep notes, Google Chat, Voice, Drive JSONs, Photo metadata)
        elif lower.endswith(".json"):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                    jdata = json.load(fp)
                    # Convert json structure to formatted text
                    extracted_text = json.dumps(jdata, indent=2)
                    source_type = "JSON_RECORD"
            except Exception:
                pass

        # D. TXT, CSV, MBOX, VCF, LOGS
        elif any(lower.endswith(ext) for ext in [".txt", ".csv", ".mbox", ".vcf", ".log", ".tsv", ".md"]):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                    extracted_text = fp.read()
                    source_type = "RAW_TEXT_MBOX"
            except Exception:
                pass

        # If text was extracted, write out clean individual transcript and index it
        if extracted_text and len(extracted_text.strip()) > 5:
            out_filename = f"{fname}.txt"
            out_path = os.path.join(OCR_OUTPUT_DIR, out_filename)
            
            try:
                with open(out_path, "w", encoding="utf-8") as out_fp:
                    out_fp.write(f"SOURCE_FILE: {fname}\n")
                    out_fp.write(f"TYPE: {source_type}\n")
                    out_fp.write(f"TIMESTAMP: {time.time()}\n")
                    out_fp.write("="*60 + "\n\n")
                    out_fp.write(extracted_text)
                
                text_extracted_count += 1
                
                # Check for high-priority hits (Sept 11, addresses, cases)
                if any(kw in extracted_text.lower() for kw in ["sep 11", "2026-09-11", "huntington", "beach blvd"]):
                    print(f"  [★ PRIORITY HIT] Extracted text from {fname} ({source_type}) -> Saved to OCR_Extracted_Text/")
                    
            except Exception as e:
                pass

    print(f"\n==================================================")
    print(f"[✓] DEEP OCR & TEXT EXTRACTION COMPLETE!")
    print(f"  - Total Transcripts Created: {text_extracted_count} files in OCR_Extracted_Text/")
    print(f"==================================================")

if __name__ == "__main__":
    run_deep_text_and_ocr_extraction()
