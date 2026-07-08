import os
import re
import sys
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    print("pdfplumber not available, trying PyPDF2")

if pdfplumber is None:
    try:
        from PyPDF2 import PdfReader as pdf_reader
        use_pypdf = True
    except ImportError:
        print("No PDF library available!")
        sys.exit(1)
else:
    use_pypdf = False

KEYWORDS = [
    'ONNI', 'G&M Oil', 'G&M', '17642', '17672', 'Beach Blvd',
    'Brink Center', 'Brink', 'Navigation Center',
    'underground storage tank', 'UST', 'leak', 'remediation',
    'permit', 'environmental site assessment', 'ESA', 'Phase I', 'Phase II',
    'well', 'groundwater', 'monitoring well',
    'benzene', 'MTBE', 'TPH', 'contamination', 'plume',
    'Huntington Beach Navigation Center', 'HBNC',
    'G&M Oil Co', 'HB Fuel', 'ONNI HB', 'ONNI HUNTINGTON BEACH',
    'Dennis Durham', 'C81252', 'E0764', 'E14813', 'E59465', 'E59466',
    'E59582', 'E59639', 'E60221', 'E61078', 'E62803', 'E62832', 'E64308',
    'Chen Yamada', 'Yamada', 'BWB SURF CITY', '303 PARTNERS',
    'WMYU', 'SA ABANOUB', 'CALLENS I', 'HB SURFACE',
    'Mercy House', 'Viet America', 'CMS-992-SHELTER',
]

# Compile case-insensitive patterns
patterns = {kw: re.compile(re.escape(kw), re.IGNORECASE) for kw in KEYWORDS}

SUMMARY_FILES = [
    'The Brink Center_ 17672 Beach Blvd, Huntington Beach, CA 92647.pdf',
    'Dennis Durham Orange County Permits WK#6.pdf',
    'Dennis Durham Orange County Permits WK#6 (2).pdf',
    'Environmental Site Assessment Huntington Beach.pdf',
    'fannie mae esa phase1 beach epa 4251.pdf',
    'geotracker.waterboards.ca.gov_csm_report_global_id=T10000018579.pdf',
    'Report loan report 17642 beach.pdf',
    'Report loan report 17642 beach (1).pdf',
    'Report loan report 17642 beach (2).pdf',
    'HBNC_Formal_Complaint_FINAL.pdf',
    'HB_IRC_Report_v1.1.pdf',
    'HB_IRC_Report_v1.1 (1).pdf',
    'UPX1978058_SupportingDocs_Chen_Yamada.pdf',
    'Meli Web mercy house rpt 2.pdf',
    'Meli Web mercy house rpt v2A.pdf',
    'Meli Web v65 report.pdf',
    'non profit data mercy house 2024-06-GSAFAC-0000355035.pdf',
    'OC_Fraud_Network_OSINT_Report_v14.pdf',
    'OC_Fraud_Network_OSINT_Report_v13.pdf',
    'Formal_Complaint_HBNC_Yamada.pdf',
    'Exhibit_A_Forensic_Well_Location_Overlay.pdf',
    'annotated_well_map.pdf',
    'GeoTracker.pdf',
    'GeoTrackerStatusDefinitions.pdf',
    'HISTORIC FILES - BULKFILE - T10000018579.BulkFile.pdf',
    'Forensic Investigation Report- Environmental Fraud and Hydrogeological Hazards at 17642 Beach Blvd, Huntington Beach.pdf',
    'Forensic Investigation into Environmental Fraud, H...pdf',
    'Huntington Beach Navigation Center  Contamination Documentation.pdf',
    'Huntington Beach Navigation Center Environmental Concerns.pdf',
    'color subsurface geo beach cameron mercypdf.pdf',
    'background well cameron beach mercy.pdf',
    'Cameron Well Drawing and History.pdf',
]

OUTPUT_DIR = r'C:\Users\HP\OneDrive\Documents\opencode_work\extracted_text'
os.makedirs(OUTPUT_DIR, exist_ok=True)

search_dirs = [
    r'G:\DL BACKUP',
    r'G:\buckp moto\Download',
]

# Collect all PDFs
all_pdfs = []
for sdir in search_dirs:
    if os.path.isdir(sdir):
        for root, dirs, files in os.walk(sdir):
            for f in files:
                if f.lower().endswith('.pdf'):
                    full = os.path.join(root, f)
                    all_pdfs.append((full, f))

print(f"Found {len(all_pdfs)} PDFs across both directories")

# Prioritize: summary files first, then everything else
priority = []
rest = []
for full_path, filename in all_pdfs:
    if any(sf.lower() == filename.lower() for sf in SUMMARY_FILES):
        priority.append((full_path, filename))
    else:
        rest.append((full_path, filename))

all_pdfs = priority + rest
print(f"Priority PDFs: {len(priority)}, Rest: {len(rest)}")

def extract_text_pdf(filepath):
    """Extract text from PDF using pdfplumber or PyPDF2"""
    text = ""
    try:
        if not use_pypdf and pdfplumber:
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    try:
                        t = page.extract_text()
                        if t:
                            text += t + "\n"
                    except:
                        pass
        else:
            reader = pdf_reader(filepath)
            for page in reader.pages:
                try:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
                except:
                    pass
    except Exception as e:
        return f"[ERROR: {str(e)}]"
    return text

results_log = []
hit_count = 0

for i, (full_path, filename) in enumerate(all_pdfs):
    try:
        fsize_mb = os.path.getsize(full_path) / (1024 * 1024)
    except:
        fsize_mb = 0

    # Skip massive files that might crash (>50MB)
    if fsize_mb > 50:
        results_log.append(f"SKIP ({fsize_mb:.1f}MB): {filename}")
        continue

    print(f"[{i+1}/{len(all_pdfs)}] {filename} ({fsize_mb:.1f}MB)...", end=' ', flush=True)
    
    text = extract_text_pdf(full_path)
    
    if text.startswith('[ERROR:'):
        print("EXTRACT FAILED")
        results_log.append(f"ERROR: {filename} - {text}")
        continue
    
    # Check for keyword hits
    hits = {}
    for kw, pattern in patterns.items():
        found = pattern.findall(text)
        if found:
            hits[kw] = len(found)
    
    if hits:
        hit_count += 1
        print(f"HIT ({', '.join(f'{k}:{v}' for k,v in hits.items())})")
        results_log.append(f"HIT [{filename}]: {hits}")
        
        # Save extracted text for priority files and hits
        if filename in [sf for sf in SUMMARY_FILES] or len(hits) >= 5:
            safe_name = filename.replace(' ', '_').replace('/', '_')[:100]
            out_path = os.path.join(OUTPUT_DIR, f"{safe_name}.txt")
            with open(out_path, 'w', encoding='utf-8') as out:
                out.write(text)
            results_log.append(f"  -> Saved text to {out_path}")
    else:
        print("no hits")
        results_log.append(f"CLEAN: {filename}")

# Write full results log
log_path = os.path.join(OUTPUT_DIR, 'pdf_scan_results.log')
with open(log_path, 'w', encoding='utf-8') as f:
    f.write(f"PDF Scan Results - {datetime.now().isoformat()}\n")
    f.write(f"Scanned: {len(all_pdfs)} PDFs, Hits: {hit_count}\n\n")
    for line in results_log:
        f.write(line + '\n')

print(f"\n=== DONE ===")
print(f"Scanned: {len(all_pdfs)} PDFs, Hits: {hit_count}")
print(f"Results log: {log_path}")
print(f"Extracted texts in: {OUTPUT_DIR}")
