"""
Comprehensive PDF OCR Scanner for HB RICO Investigation
Targets: G&M Oil (#124, 17472 Beach), ONNI, 17642 Beach Blvd, Yamada, environmental reports
Uses: PyMuPDF + Vertex AI Gemini for OCR with flag detection
"""
import os, sys, time, re, json, argparse
from datetime import datetime
import fitz  # PyMuPDF

# --- Config ---
OUTPUT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work\ocr_output"
LOG_FILE = os.path.join(OUTPUT_DIR, "ocr_scan_log.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FLAG_TERMS = [
    r'\bONNI\b', r'G\s*&\s*M\s*Oil', r'\b17642\b', r'\b17472\b',
    r'Cameron\s*Ln', r'Yamada', r'cesspool', r'contaminat',
    r'variance', r'waiver', r'\bUST\b', r'GeoTracker',
    r'asbestos', r'lead.based', r'pesticide', r'herbicide',
    r'groundwater', r'aquifer', r'plume', r'benzene', r'MTBE',
    r'Mitsuru', r'navigation\s*center', r'homeless\s*shelter',
    r'HBNC', r'Beach\s*Blvd', r'well', r'irrigation',
    r'underground\s*storage\s*tank', r'leaking', r'LUST',
    r'Phase\s*[I1]\s*(Environmental|ESA)',
    r'demolition', r'excavation', r'septic',
    r'water\s*board', r'RWQCB', r'DTSC', r'EPA',
    r'environmental\s*(fraud|hazard|impact)', r'mitigation',
    r'Santa\s*Ana\s*Regional', r'discharge', r'violation',
    r'\bAPN\b', r'assessor', r'parcel',
]

# Permit-specific terms
PERMIT_FLAGS = [
    r'building\s*permit', r'grading\s*permit', r'encroachment',
    r'conditional\s*use', r'CUP\b', r'variance', r'zoning',
    r'setback', r'easement', r'right.of.way',
    r'plan\s*check', r'structural', r'foundation',
    r'plumbing', r'electrical', r'mechanical',
    r'fire\s*sprinkler', r'ADA\b', r'accessibility',
    r'CEQA\b', r'NEPA\b', r'environmental\s*review',
    r'coastal\s*commission', r'CCC\b',
]

PRIORITY_PATTERNS = [
    r'ONNI', r'G.M.Oil', r'17472', r'17642', r'17631',
    r'Yamada', r'forensic', r'phase.*(1|I|one).*environmental',
    r'site.assessment', r'esa', r'geotracker', r'well.data',
    r'permit', r'variance', r'waiver', r'criminal.*referral',
    r'HBNC', r'navigation.*center', r'environmental.*fraud',
    r'hydrogeological', r'contamination', r'UST',
    r'Chen', r'Mitsuru',
]

# --- OCR Engine ---
class GeminiOCR:
    """Vertex AI Gemini OCR engine using google.genai"""
    def __init__(self):
        import google.auth
        import google.genai as genai
        from google.genai import types as gtypes
        creds, proj = google.auth.default()
        self.client = genai.Client(vertexai=True, project=proj, location="us-central1")
        self.model = "gemini-2.5-flash"
        self.types = gtypes
        print(f"[OCR] Connected to Vertex AI, project={proj}, model={self.model}")

    def ocr_page(self, image_bytes: bytes, page_num: int, context: str = "") -> str:
        """OCR a single page image with Gemini"""
        prompt = f"""You are an OCR and forensic investigation assistant. Extract ALL text from this document page.

This is page {page_num}. {context}

CRITICAL: Return every visible word exactly as it appears. Include:
- All proper names, addresses, APN numbers, dates, dollar amounts
- All regulatory citations, permit numbers, case numbers
- All environmental terms, contaminant names, concentration levels

If any of these flagged terms appear, list them at the top under [FLAGS]:
G&M Oil, ONNI, 17642 Beach Blvd, 17472 Beach Blvd, Cameron Lane, Yamada, Mitsuru,
cesspool, contamination, asbestos, lead-based paint, pesticides, groundwater, UST,
GeoTracker, variance, waiver, permit, environmental fraud, well, irrigation,
HBNC, navigation center, homeless shelter, demolition, septic, excavation, APN

Then output the full text under [TEXT].
"""
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        self.types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                        prompt,
                    ],
                )
                return response.text
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait = (attempt + 1) * 15
                    print(f"  Rate limit, waiting {wait}s...")
                    time.sleep(wait)
                elif attempt < 2:
                    print(f"  Retry {attempt+2}... ({str(e)[:80]})")
                    time.sleep(5)
                else:
                    raise

    def ocr_pdf_direct(self, pdf_data: bytes, filename: str) -> str:
        """Send entire PDF directly to Gemini (for smaller files)"""
        prompt = f"""You are an OCR and forensic investigation assistant.
OCR this entire document: {filename}

Extract ALL text. For ANY mentions of these flagged terms, list them at the top under [FLAGS]:
G&M Oil, ONNI, 17642 Beach Blvd, 17472 Beach Blvd, Cameron Lane, Yamada, Mitsuru,
cesspool, contamination, asbestos, lead-based paint, pesticides, UST, GeoTracker,
variance, waiver, permit, environmental fraud, well, irrigation, HBNC,
navigation center, homeless shelter, demolition, septic, excavation, APN

Then output the full text under [TEXT].
"""
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        self.types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
                        prompt,
                    ],
                )
                return response.text
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait = (attempt + 1) * 15
                    print(f"  Rate limit, waiting {wait}s...")
                    time.sleep(wait)
                elif attempt < 2:
                    print(f"  Retry {attempt+2}... ({str(e)[:80]})")
                    time.sleep(5)
                else:
                    raise


def scan_flags(text: str) -> list:
    """Scan extracted text for flag terms and return matched terms"""
    found = []
    for pattern in FLAG_TERMS + PERMIT_FLAGS:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found.extend(matches)
        except:
            pass
    return list(set(found))

def get_priority_score(filename: str) -> int:
    """Higher score = higher priority for processing"""
    score = 0
    fname_lower = filename.lower()
    for i, pat in enumerate(PRIORITY_PATTERNS):
        if re.search(pat, fname_lower, re.IGNORECASE):
            score += len(PRIORITY_PATTERNS) - i
    return score

def process_pdf(fpath: str, ocr: GeminiOCR, stats: dict) -> dict:
    """Process a single PDF: OCR it and scan for flags"""
    result = {
        "file": fpath,
        "filename": os.path.basename(fpath),
        "size_mb": round(os.path.getsize(fpath) / 1e6, 2),
        "status": "pending",
        "flags_found": [],
        "output_file": "",
        "text_length": 0,
        "error": None,
    }

    try:
        fname = os.path.basename(fpath)
        safe_name = re.sub(r'[^\w\-\.]', '_', fname)[:60]
        out_txt = os.path.join(OUTPUT_DIR, f"ocr_{safe_name}.txt")

        # Skip if already processed
        if os.path.exists(out_txt) and os.path.getsize(out_txt) > 100:
            print(f"  [SKIP] Already processed: {out_txt}")
            text = open(out_txt, "r", encoding="utf-8", errors="replace").read()
            flags = scan_flags(text)
            result["status"] = "cached"
            result["flags_found"] = flags
            result["output_file"] = out_txt
            result["text_length"] = len(text)
            stats["cached"] += 1
            return result

        # For larger PDFs (>15MB), do page-by-page
        if result["size_mb"] > 15:
            print(f"  Large PDF ({result['size_mb']:.1f} MB), processing page-by-page...")
            doc = fitz.open(fpath)
            total_pages = len(doc)
            print(f"  Total pages: {total_pages}")

            all_text = []
            for page_num in range(total_pages):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")

                page_text = ocr.ocr_page(img_bytes, page_num + 1, f"Document: {fname}")
                all_text.append(f"\n--- PAGE {page_num+1} ---\n{page_text}")

                if (page_num + 1) % 10 == 0:
                    print(f"  Page {page_num+1}/{total_pages} done")
                if (page_num + 1) % 5 == 0:
                    time.sleep(2)  # Rate limit buffer

            doc.close()
            text = "\n".join(all_text)

        # Smaller PDFs: send direct
        else:
            print(f"  Small PDF ({result['size_mb']:.1f} MB), direct OCR...")
            with open(fpath, "rb") as f:
                pdf_data = f.read()
            text = ocr.ocr_pdf_direct(pdf_data, fname)

        # Save output
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(text)

        flags = scan_flags(text)
        result["status"] = "success"
        result["flags_found"] = flags
        result["output_file"] = out_txt
        result["text_length"] = len(text)
        stats["success"] += 1
        print(f"  [OK] {len(text)} chars, {len(flags)} flags: {flags[:8]}")

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:200]
        stats["errors"] += 1
        print(f"  [ERR] {e}")

    return result

def scan_directories(dirs: list) -> list:
    """Find all PDFs in given directories with priority scoring"""
    all_pdfs = []
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().endswith('.pdf'):
                    fpath = os.path.join(root, f)
                    priority = get_priority_score(f)
                    all_pdfs.append((priority, fpath))
    all_pdfs.sort(reverse=True, key=lambda x: x[0])
    return [fp for _, fp in all_pdfs]

def main():
    target_dirs = [
        r"G:\DL BACKUP",
        r"G:\buckp moto\Download",
        r"G:\619onedrivepost\backup tclphone\dls",
        r"G:\BACKUP ASUS 24\DOCS2",
    ]

    print("=" * 60)
    print("HB RICO PDF OCR Scanner")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Discover PDFs
    print("\n[1] Scanning directories...")
    pdfs = scan_directories(target_dirs)
    print(f"  Found {len(pdfs)} PDFs total")

    # Show top priority files
    print("\n[2] Top priority files:")
    for i, fp in enumerate(pdfs[:20]):
        score = get_priority_score(fp)
        fname = os.path.basename(fp)
        size = os.path.getsize(fp) / 1e6
        print(f"  P{score:3d}  {size:8.1f} MB  {fname[:80]}")

    if len(pdfs) > 20:
        print(f"  ... and {len(pdfs) - 20} more")

    # Initialize OCR
    print("\n[3] Initializing Vertex AI OCR...")
    try:
        ocr = GeminiOCR()
    except Exception as e:
        print(f"  [FATAL] Could not initialize OCR: {e}")
        sys.exit(1)

    # Process files
    print(f"\n[4] Processing PDFs...")
    stats = {"total": len(pdfs), "success": 0, "errors": 0, "cached": 0, "skipped": 0}
    all_results = []

    for i, fp in enumerate(pdfs):
        fname = os.path.basename(fp)
        priority = get_priority_score(fp)
        size = os.path.getsize(fp) / 1e6

        print(f"\n[{i+1}/{len(pdfs)}] P{priority} {size:.1f}MB {fname[:70]}")

        result = process_pdf(fp, ocr, stats)
        all_results.append(result)

        # Save intermediate log
        if (i + 1) % 10 == 0:
            with open(LOG_FILE, "w") as f:
                json.dump({"stats": stats, "results": all_results}, f, indent=2, default=str)

        # Rate limit between files
        if i < len(pdfs) - 1:
            time.sleep(2)

    # Final save
    with open(LOG_FILE, "w") as f:
        json.dump({"stats": stats, "results": all_results}, f, indent=2, default=str)

    # Summary
    print("\n" + "=" * 60)
    print("SCAN COMPLETE")
    print(f"  Total PDFs:  {stats['total']}")
    print(f"  Success:     {stats['success']}")
    print(f"  Cached:      {stats['cached']}")
    print(f"  Errors:      {stats['errors']}")
    print(f"  Output dir:  {OUTPUT_DIR}")
    print(f"  Log file:    {LOG_FILE}")
    print("=" * 60)

    # Print files with flags found
    flagged = [r for r in all_results if r.get("flags_found")]
    if flagged:
        print(f"\n[FLAGGED FILES] {len(flagged)} files with matches:")
        for r in flagged:
            fname = r["filename"][:60]
            flags = r.get("flags_found", [])
            print(f"  {fname}")
            print(f"    Flags: {', '.join(flags[:10])}")
            if len(flags) > 10:
                print(f"    ... and {len(flags)-10} more")
    else:
        print("\n[NO FLAGS FOUND]")

if __name__ == "__main__":
    main()
