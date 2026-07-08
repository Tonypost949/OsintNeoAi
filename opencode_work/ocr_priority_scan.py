"""
Priority OCR scan: Top 21 forensic/environmental PDFs for RICO investigation.
"""
import os, sys, time, re, json
from datetime import datetime
import fitz
import google.auth
import google.genai as genai
from google.genai import types as gtypes

OUTPUT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work\ocr_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PRIORITY_FILES = [
    r"G:\buckp moto\Download\Forensic Investigation Report- Environmental Fraud and Hydrogeological Hazards at 17642 Beach Blvd, Huntington Beach.pdf",
    r"G:\DL BACKUP\SITE ASSESSMENT REPORT  - SITE ASSESSMENT REPORT - Site Assessment Report - 17631 Cameron Ln - 18330.0006.00.pdf",
    r"G:\DL BACKUP\UPX1978058_SupportingDocs_Chen_Yamada.pdf",
    r"G:\DL BACKUP\T10000018579_2026-Jun-02-112324\HISTORIC FILES - PHASE I ENVIRONMENTAL SITE ASSESSMENT - T10000018579.20200318.Phase I Environmental Site Assessment.pdf",
    r"G:\DL BACKUP\T10000018579_2026-Jun-02-112324\HISTORIC FILES - SITE ASSESSMENT REPORT - T10000018579.20200625.Site Assessment Report.pdf",
    r"G:\DL BACKUP\SITE ASSESSMENT REPORT  - SITE ASSESSMENT REPORT - Additonal Assessment Report 17642 Beach Blvd - 18334.0004.00.pdf",
    r"G:\buckp moto\Download\Exhibit_A_Forensic_Well_Location_Overlay.pdf",
    r"G:\DL BACKUP\20250515181253092 17631 Cameron Ln - Electrical.pdf",
    r"G:\buckp moto\Download\andrew-do-forensic-audit-report-commissioned-by-county-phase-1.pdf",
    r"G:\buckp moto\Download\Future Development of 17642 Beach Blvd. - NO ACTION TAKEN (2).pdf",
    r"G:\DL BACKUP\Huntington Beach Navigation Center_ A Critical Analysis of Environmental Contamination and Public Health Risks.pdf",
    r"G:\DL BACKUP\SITE SUMMARY AND RECOMMENDATIONS - 17642 Beach Blvd- Site Summary and Recommendations - 18334.0004.00.pdf",
    r"G:\DL BACKUP\well_map_color_subsurface_geo_beach_cameron_mercypdf_1771475692453.pdf",
    r"G:\DL BACKUP\Copy_of_full_info_well_17642_beach_1771475692432.pdf",
    r"G:\DL BACKUP\Copy of full info well 17642 beach.pdf",
    r"G:\DL BACKUP\Copy of update 17642 wells data.pdf",
    r"G:\DL BACKUP\Cameron_Tract_Wells__1940s_&_Undated_(1)_1771475692334.pdf",
    r"G:\619onedrivepost\backup tclphone\dls\Huntington-Beach-Military-Equipment.pdf",
    r"G:\619onedrivepost\backup tclphone\dls\sb-1928-report-to-legislature-july-2018.pdf",
    r"G:\DL BACKUP\Huntington Beach Navigation Center Contamination Documentation.pdf",
    r"G:\DL BACKUP\Huntington Beach Navigation Center Contamination Documentation-1.pdf",
    r"G:\DL BACKUP\Huntington Beach Navigation Center Contamination Documentation-2.pdf",
    r"G:\DL BACKUP\Huntington Beach Navigation Center Contamination Documentation-3.pdf",
    r"G:\DL BACKUP\Huntington Beach Navigation Center Contamination Documentation-4.pdf",
    r"G:\buckp moto\Download\dimarcello Actionable Plan for Criminal Activity.pdf",
]

FLAG_TERMS = [
    r"\bONNI\b", r"G\s*&\s*M\s*Oil", r"\b17642\b", r"\b17472\b",
    r"Cameron\s*Ln?", r"Yamada", r"Mitsuru", r"cesspool",
    r"contaminat", r"asbestos", r"lead.based", r"pesticide",
    r"groundwater", r"aquifer", r"plume", r"benzene",
    r"\bUST\b", r"GeoTracker", r"LUST\b", r"septic",
    r"variance", r"waiver", r"demolition",
    r"HBNC", r"navigation\s*center", r"homeless\s*shelter",
    r"\bAPN\b", r"\bwell\b.*\bdata\b", r"irrigation",
    r"underground\s*storage\s*tank",
    r"RWQCB", r"DTSC", r"water\s*board",
    r"environmental\s*fraud", r"hydrogeological",
    r"structural\s*variance", r"building\s*permit",
    r"grading\s*permit", r"conditional\s*use",
    r"CEQA", r"NEPA", r"coastal\s*commission",
    r"\bChen\b",
]

def scan_flags(text):
    found = []
    for p in FLAG_TERMS:
        try:
            m = re.findall(p, text, re.IGNORECASE)
            if m:
                found.extend(m)
        except:
            pass
    return list(set(found))

def safe_filename(fname):
    return re.sub(r"[^\w\-\.]", "_", fname)[:55]

def main():
    print("Connecting to Vertex AI...")
    creds, proj = google.auth.default()
    client = genai.Client(vertexai=True, project=proj, location="us-central1")
    print(f"Connected. Project={proj}\n")

    results = []
    stats = {"success": 0, "errors": 0, "skipped": 0}

    for i, fpath in enumerate(PRIORITY_FILES):
        if not os.path.exists(fpath):
            print(f"[{i+1}/{len(PRIORITY_FILES)}] NOT FOUND: {os.path.basename(fpath)}")
            stats["skipped"] += 1
            continue

        fname = os.path.basename(fpath)
        size_mb = os.path.getsize(fpath) / 1e6
        safe = safe_filename(fname)
        out_txt = os.path.join(OUTPUT_DIR, f"ocr_{safe}.txt")

        print(f"\n[{i+1}/{len(PRIORITY_FILES)}] {size_mb:.1f}MB {fname[:60]}")

        # Check cache
        if os.path.exists(out_txt) and os.path.getsize(out_txt) > 200:
            text = open(out_txt, "r", encoding="utf-8", errors="replace").read()
            flags = scan_flags(text)
            print(f"  [CACHED] {len(text)} chars, {len(flags)} flags")
            results.append({"file": fname, "flags": flags, "size": len(text), "status": "cached"})
            stats["success"] += 1
            continue

        try:
            if size_mb > 15:
                print(f"  Large file, page-by-page (max 30 pages)...")
                doc = fitz.open(fpath)
                pages = len(doc)
                all_text = []
                for pn in range(min(pages, 30)):
                    try:
                        pix = doc[pn].get_pixmap(dpi=150)
                        img_bytes = pix.tobytes("png")
                        prompt = f"OCR this page {pn+1} of {fname}. Extract all text, addresses, APN numbers, permit numbers, contaminant names, concentrations."
                        resp = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[
                                gtypes.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                                prompt,
                            ],
                        )
                        all_text.append(f"--- PAGE {pn+1} ---\n{resp.text}")
                    except Exception as pe:
                        all_text.append(f"--- PAGE {pn+1} ERROR: {pe} ---")
                    if (pn + 1) % 5 == 0:
                        print(f"  Page {pn+1}/{min(pages, 30)} done")
                        time.sleep(2)
                doc.close()
                text = "\n".join(all_text)
            else:
                print(f"  Direct PDF OCR...")
                with open(fpath, "rb") as f:
                    pdf_data = f.read()
                prompt = f"OCR this document: {fname}. Extract ALL text. Flag any mentions of: G&M Oil, ONNI, 17642 Beach Blvd, 17472 Beach Blvd, Yamada, Mitsuru, APN numbers, variance, waiver, UST, well data, contamination, asbestos, lead paint, pesticides, cesspool, HBNC, navigation center, homeless shelter, environmental fraud, hydrogeological hazards, demolition, excavation."
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        gtypes.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
                        prompt,
                    ],
                )
                text = resp.text

            with open(out_txt, "w", encoding="utf-8") as f:
                f.write(text)

            flags = scan_flags(text)
            print(f"  [OK] {len(text)} chars, {len(flags)} flags: {flags[:8]}")
            results.append({"file": fname, "flags": flags, "size": len(text), "status": "success"})
            stats["success"] += 1

        except Exception as e:
            err = str(e)[:150]
            print(f"  [ERR] {err}")
            results.append({"file": fname, "flags": [], "size": 0, "status": "error", "error": err})
            stats["errors"] += 1

        time.sleep(2)

    # Save full results
    log_path = os.path.join(OUTPUT_DIR, "ocr_priority_log.json")
    with open(log_path, "w") as f:
        json.dump({"stats": stats, "results": results}, f, indent=2, default=str)

    # Print summary
    print("\n" + "=" * 60)
    print("PRIORITY OCR SCAN COMPLETE")
    print(f"  Success: {stats['success']} | Errors: {stats['errors']} | Skipped: {stats['skipped']}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Log: {log_path}")
    print()

    flagged = [r for r in results if r.get("flags")]
    print(f"FILES WITH FLAG MATCHES: {len(flagged)}")
    print("-" * 60)
    for r in flagged:
        unique_flags = list(set(r["flags"]))
        print(f"  [{len(unique_flags)} flags] {r['file'][:65]}")
        print(f"    {sorted(unique_flags)[:12]}")
        if len(unique_flags) > 12:
            print(f"    ... +{len(unique_flags)-12} more")
    print("=" * 60)

if __name__ == "__main__":
    main()
