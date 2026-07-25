import PyPDF2
import re

paths = [
    r"C:\Users\HP\OneDrive\Documents\xray shoulder dimarcello\DonnettaLWilburn-TruthFinderReport.pdf",
    r"C:\Users\HP\OneDrive\Documents\SharedAsLink\NathanielAMcQuown-TruthfinderReport.pdf",
    r"C:\Users\HP\OneDrive\Documents\xray shoulder dimarcello\DoOHoang-TruthFinderReport.pdf",
    r"C:\Users\HP\OneDrive\Documents\xray shoulder dimarcello\FranciscoAGarcia-TruthFinderReport (2).pdf",
    r"C:\Users\HP\OneDrive\Documents\tapk\OSINTNeoAI\pypdfsheet\16381WhittierLn-TruthFinderReport-14ce29873569bc0f.pdf",
    r"C:\Users\HP\OneDrive\Documents\tapk\OSINTNeoAI\pypdfsheet\GeoffreyCNutt-TruthFinderReport-14ce29873569bc0f.pdf",
    r"C:\Users\HP\OneDrive\Documents\tapk\OSINTNeoAI\pypdfsheet\GregScottNutt-TruthFinderReport-14ce29873569bc0f.pdf"
]

with open(r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tf_output.txt", "w", encoding="utf-8") as f:
    for p in paths:
        try:
            reader = PyPDF2.PdfReader(p)
            text = ''.join([page.extract_text() for page in reader.pages])
            
            # Look for addresses in CA
            addresses = set(re.findall(r'\d+\s+[A-Za-z\s]+(?:Ave|Blvd|St|Dr|Ln|Road|Rd|Way|Ct).*?CA\s+\d{5}', text, re.IGNORECASE))
            f.write(f"File: {p}\n")
            if addresses:
                f.write(f"CA Addresses found: {addresses}\n")
            else:
                generic = set(re.findall(r'\d+\s+[A-Za-z\s]+(?:Ave|Blvd|St|Dr|Ln|Road|Rd|Way|Ct|Cir)', text, re.IGNORECASE))
                f.write(f"Addresses found: {generic}\n")
            f.write("-" * 50 + "\n")
        except Exception as e:
            f.write(f"Error on {p}: {e}\n")
