import os, re, time, sys
import google.auth
import google.genai as genai
from google.genai import types as gtypes

OUT = r"C:\Users\HP\OneDrive\Documents\opencode_work\ocr_output"
os.makedirs(OUT, exist_ok=True)

files = [
    (r"G:\DL BACKUP\ReplitExport-amd949609\Well-Mapper\attached_assets\Cameron_Tract_Wells__1940s_&_Undated_(1)_1771475692334.pdf", "Cameron Tract Wells 1940s"),
    (r"G:\DL BACKUP\ReplitExport-amd949609\Well-Mapper\attached_assets\Copy_of_full_info_well_17642_beach_1771475692432.pdf", "17642 beach well info"),
    (r"G:\buckp moto\Download\Copy of full info well 17642 beach.pdf", "17642 beach well info 2"),
    (r"G:\buckp moto\Download\Copy of update 17642 wells data.pdf", "17642 wells data update"),
    (r"G:\DL BACKUP\T10000018579_2026-Jun-02-112324\SITE SUMMARY AND RECOMMENDATIONS - 17642 Beach Blvd- Site Summary and Recommendations Final.pdf", "17642 site summary final"),
    (r"G:\DL BACKUP\T10000018579_2026-Jun-02-112324\SITE SUMMARY AND RECOMMENDATIONS - Cameron Ln Property Site Summary and Recommendation.pdf", "Cameron Ln site summary"),
    (r"G:\buckp moto\Download\Forensic Investigation Report- Environmental Fraud and Hydrogeological Hazards at 17642 Beach Blvd, Huntington Beach.pdf", "17642 forensic investigation"),
    (r"G:\buckp moto\Download\andrew-do-forensic-audit-report-commissioned-by-county-phase-1.pdf", "Andrew Do forensic audit"),
    (r"G:\buckp moto\Download\Future Development of 17642 Beach Blvd. - NO ACTION TAKEN (2).pdf", "17642 future development"),
    (r"G:\DL BACKUP\Huntington Beach Navigation Center_ A Critical Analysis of Environmental Contamination and Public Health Risks.pdf", "HBNC contamination analysis"),
    (r"G:\DL BACKUP\20250515181253092 17631 Cameron Ln - Electrical.pdf", "17631 Cameron electrical permit"),
    (r"G:\buckp moto\Download\Exhibit_A_Forensic_Well_Location_Overlay.pdf", "Forensic well overlay"),
    (r"G:\buckp moto\Download\GPR_Field_Use_Well_Target_Map.pdf", "GPR well target map"),
    (r"G:\buckp moto\Download\Exhibit_A_With_Grid_And_Scale_Verification.pdf", "Grid scale verification"),
    (r"G:\buckp moto\Download\HB_IRC_Report_v1.1.pdf", "HB IRC Report"),
]

FLAG_PATTERNS = [
    (r"ONNI", "ONNI"),
    (r"G\s*&?\s*M\s*Oil", "G&M Oil"),
    (r"17642", "17642 Beach Blvd"),
    (r"17472", "17472 Beach Blvd"),
    (r"Cameron", "Cameron Lane"),
    (r"Yamada", "Yamada"),
    (r"Mitsuru", "Mitsuru"),
    (r"cesspool", "cesspool"),
    (r"contaminat", "contamination"),
    (r"asbestos", "asbestos"),
    (r"lead.based", "lead-based paint"),
    (r"pesticide", "pesticide"),
    (r"groundwater", "groundwater"),
    (r"UST", "UST"),
    (r"GeoTracker", "GeoTracker"),
    (r"septic", "septic"),
    (r"variance", "variance"),
    (r"waiver", "waiver"),
    (r"HBNC", "HBNC"),
    (r"navigation center", "navigation center"),
    (r"homeless shelter", "homeless shelter"),
    (r"APN", "APN"),
    (r"irrigation", "irrigation"),
    (r"demolition", "demolition"),
    (r"well", "well"),
    (r"water board", "water board"),
    (r"CEQA", "CEQA"),
    (r"NEPA", "NEPA"),
    (r"Chen", "Chen"),
    (r"environmental fraud", "environmental fraud"),
    (r"building permit", "building permit"),
    (r"grading permit", "grading permit"),
    (r"coastal commission", "coastal commission"),
    (r"RWQCB", "RWQCB"),
    (r"DTSC", "DTSC"),
    (r"benzene", "benzene"),
    (r"MTBE", "MTBE"),
    (r"plume", "plume"),
    (r"aquifer", "aquifer"),
    (r"LUST", "LUST"),
    (r"discharge", "discharge"),
    (r"violation", "violation"),
    (r"cleanup", "cleanup"),
    (r"remediation", "remediation"),
    (r"E\d{4,5}", "permit E-number"),
    (r"permit #", "permit #"),
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

def safe_name(fname):
    return re.sub(r"[^\w\-\.]", "_", fname)[:55]

print("Connecting to Vertex AI...")
creds, proj = google.auth.default()
client = genai.Client(vertexai=True, project=proj, location="us-central1")
print(f"Project: {proj}\n")

stats = {"ok": 0, "err": 0, "cached": 0, "missing": 0}

for fpath, desc in files:
    if not os.path.exists(fpath):
        print(f"[MISSING] {desc}")
        stats["missing"] += 1
        continue

    fname = os.path.basename(fpath)
    size = os.path.getsize(fpath) / 1e6
    safe = safe_name(fname)
    out_txt = os.path.join(OUT, f"ocr_{safe}.txt")

    # Check cache
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 200:
        text = open(out_txt, encoding="utf-8", errors="replace").read()
        flags = scan_flags(text)
        print(f"[CACHED] {desc}: {len(text)} chars, {len(flags)} flag categories")
        stats["cached"] += 1
        continue

    print(f"[{desc}] {size:.2f}MB ...", end=" ", flush=True)
    try:
        with open(fpath, "rb") as f:
            pdf_data = f.read()

        prompt = f"OCR document: {fname}. Extract ALL visible text verbatim. At the top, list any mentions of: ONNI, G&M Oil, 17472, 17642, Cameron, Yamada, Mitsuru, APN numbers, permit numbers (like E0764), well data, contamination, UST, GeoTracker, variance, waiver, HBNC, navigation center, homeless shelter, environmental violations."
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[gtypes.Part.from_bytes(data=pdf_data, mime_type="application/pdf"), prompt],
        )
        text = resp.text
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(text)

        flags = scan_flags(text)
        print(f"OK ({len(text)} chars)")
        if flags:
            for label, vals in sorted(flags.items()):
                val_str = ", ".join(vals[:2])
                print(f"    [{label}]: {val_str}")
        stats["ok"] += 1
    except Exception as e:
        print(f"ERR: {str(e)[:120]}")
        stats["err"] += 1

    time.sleep(2)

print(f"\nDONE: {stats['ok']} ok, {stats['err']} err, {stats['cached']} cached, {stats['missing']} missing")
