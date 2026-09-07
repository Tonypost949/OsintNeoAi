"""
index_edr_2025_real.py
Scans and indexes the 51 authoritative EDR documents downloaded from Google Drive
folder Private_EDR_2025_Real (1YWhP6j3OEIzar4xL8TrZVdSbiSpI6YCU).
Computes SHA-256 hashes, extracts page counts, target addresses, and generates
reports/EDR_2025_REAL_MASTER_INDEX.md & .json.
"""
import os
import json
import hashlib
import fitz

EDR_DIR = r"c:\OsintNeoAi\evidence\edr_2025_real"
OUTPUT_MD = r"c:\OsintNeoAi\reports\EDR_2025_REAL_MASTER_INDEX.md"
OUTPUT_JSON = r"c:\OsintNeoAi\reports\EDR_2025_REAL_MASTER_INDEX.json"

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def analyze_file(fname):
    fpath = os.path.join(EDR_DIR, fname)
    size_bytes = os.path.getsize(fpath)
    sha256 = get_sha256(fpath)
    
    info = {
        "filename": fname,
        "size_bytes": size_bytes,
        "size_kb": round(size_bytes / 1024.0, 2),
        "sha256": sha256,
        "type": "OTHER",
        "page_count": 0,
        "target_address": "N/A",
        "inquiry_number": "N/A",
        "date": "N/A",
        "summary": ""
    }
    
    if fname.lower().endswith('.pdf'):
        try:
            doc = fitz.open(fpath)
            info["page_count"] = len(doc)
            text_p0 = doc[0].get_text('text') if len(doc) > 0 else ""
            
            # Detect document type
            if "Sanborn" in fname or "Sanborn" in text_p0:
                info["type"] = "SANBORN_FIRE_INSURANCE_MAP"
            elif "Aerial Photo Decade" in text_p0 or "Aerial" in fname:
                info["type"] = "HISTORICAL_AERIAL_DECADE"
            elif "Historical Topo" in text_p0 or "Topo" in fname:
                info["type"] = "HISTORICAL_TOPOGRAPHIC_MAP"
            elif "Property Tax Map" in text_p0:
                info["type"] = "PROPERTY_TAX_MAP_REPORT"
            elif "Building Permit" in text_p0:
                info["type"] = "BUILDING_PERMIT_REPORT"
            elif "Radius Map" in text_p0 or "SUMMARY_RADIUS" in fname:
                info["type"] = "EDR_RADIUS_MAP_REPORT"
            elif "Historical Survey" in fname:
                info["type"] = "HISTORICAL_SURVEY_APPENDIX"
            elif "Site Assessment" in text_p0:
                info["type"] = "SITE_ASSESSMENT_REPORT"
            else:
                info["type"] = "EDR_ENVIRONMENTAL_RECORD"
                
            # Extract Inquiry Number and Address
            for line in text_p0.split('\n'):
                line_str = line.strip()
                if "Inquiry Number:" in line_str:
                    info["inquiry_number"] = line_str.replace("Inquiry Number:", "").strip()
                elif "7887036" in line_str or "7969270" in line_str or "7867953" in line_str:
                    if info["inquiry_number"] == "N/A":
                        info["inquiry_number"] = line_str
                if any(kw in line_str for kw in ["BEACH BLVD", "CAMERON LN", "SHADY", "GARDEN GROVE"]):
                    if info["target_address"] == "N/A":
                        info["target_address"] = line_str
                        
            info["summary"] = f"{info['type']} ({info['page_count']} pages)"
        except Exception as e:
            info["summary"] = f"Error reading PDF: {e}"
            
    elif fname.lower().endswith('.rtf'):
        info["type"] = "CITY_DIRECTORY_RTF"
        info["summary"] = "EDR City Directory reverse occupant listing"
        
    return info

def main():
    files = sorted(os.listdir(EDR_DIR))
    records = []
    
    print(f"Indexing {len(files)} files in {EDR_DIR}...")
    for f in files:
        if f.endswith('.partial') or f.startswith('.'):
            continue
        rec = analyze_file(f)
        records.append(rec)
        print(f"  [+] {rec['filename']} | {rec['type']} | {rec['page_count']} pgs | {rec['target_address']}")
        
    # Write JSON
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)
    print(f"[+] Saved JSON index to {OUTPUT_JSON}")
    
    # Write Markdown
    md_lines = [
        "# 📁 EDR 2025 Master Environmental Evidence Index",
        "",
        f"Authoritative inventory of all **{len(records)}** environmental forensic assets retrieved from Google Drive folder `Private_EDR_2025_Real` (`1YWhP6j3OEIzar4xL8TrZVdSbiSpI6YCU`).",
        "",
        "| File Name | Category / Type | Pages | Size (KB) | Target Address / Inquiry | SHA-256 (First 12) |",
        "| :--- | :--- | :---: | :---: | :--- | :--- |"
    ]
    for r in records:
        h12 = r['sha256'][:12] + "..."
        md_lines.append(f"| `{r['filename']}` | **{r['type']}** | {r['page_count']} | {r['size_kb']} | {r['target_address']} ({r['inquiry_number']}) | `{h12}` |")
        
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    print(f"[+] Saved Markdown index to {OUTPUT_MD}")

if __name__ == '__main__':
    main()
