import zipfile
import re

filepath = r"C:\Users\HP\Downloads\Data-Ingestion-and-Extraction-Plan.docx"
try:
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        xml_content = zip_ref.read('word/document.xml').decode('utf-8')
        # Extract text within <w:t> tags
        text_matches = re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml_content)
        full_text = "\n".join(text_matches)
        
        # Write to scratch file
        out_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\ingestion_plan_text.txt"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"Successfully wrote {len(text_matches)} text segments to ingestion_plan_text.txt")
except Exception as e:
    print(f"Error: {e}")
