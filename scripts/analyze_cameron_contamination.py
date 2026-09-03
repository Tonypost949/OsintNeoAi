import os
import json
import re
from pathlib import Path

pdf_path = Path(r'C:\OsintNeoAi\scratch\site_assessment_17631_cameron.pdf')

print("=== GEOTRACKER SITE ASSESSMENT REPORT PDF EVALUATION ENGINE ===")
print(f"Target PDF: {pdf_path} ({pdf_path.stat().st_size / (1024*1024):.2f} MB)")

# Install PyMuPDF / pypdf if needed
try:
    import fitz # PyMuPDF
    fitz_available = True
    print("✓ PyMuPDF (fitz) active.")
except ImportError:
    fitz_available = False
    print("[-] PyMuPDF not installed. Installing pypdf / PyMuPDF...")

extracted_text = []

if fitz_available:
    doc = fitz.open(pdf_path)
    print(f"Total Pages in Site Assessment Report: {len(doc)}")
    
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        extracted_text.append({
            'page': page_num + 1,
            'text': text
        })
        
    full_str = "\n".join([f"--- PAGE {p['page']} ---\n{p['text']}" for p in extracted_text])
    out_txt = Path(r'C:\OsintNeoAi\evidence\geotracker_17631_cameron_full_text.txt')
    out_txt.write_text(full_str, encoding='utf-8')
    print(f"✓ Saved full extracted PDF text ({len(full_str)} chars) to: {out_txt}")
    
    # Search for contaminant keywords: PCE, TCE, Lead, Benzene, UST, Plume, Groundwater, VOC
    contaminants = ['PCE', 'TCE', 'lead', 'benzene', 'tetrachloroethene', 'trichloroethene', 'ust', 'underground storage tank', 'plume', 'voc', 'soil vapor', 'groundwater', 'mercy house', 'city of huntington beach']
    
    matches = []
    for p in extracted_text:
        text_lower = p['text'].lower()
        found_terms = [t for t in contaminants if t in text_lower]
        if found_terms:
            matches.append({
                'page': p['page'],
                'terms': found_terms,
                'snippet': p['text'][:400].replace('\n', ' ')
            })
            
    out_json = Path(r'C:\OsintNeoAi\data\geotracker_17631_cameron_contamination_analysis.json')
    out_json.write_text(json.dumps(matches, indent=2), encoding='utf-8')
    print(f"✓ Total Contamination Keyword Matches Found: {len(matches)} pages.")
    print(f"✓ Analysis report saved to: {out_json}")
