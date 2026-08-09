import fitz
import os

pdf_path = r'G:\DL BACKUP\non profit data mercy house 2024-06-GSAFAC-0000355035.pdf'
output_dir = r'C:\Users\HP\OneDrive\Documents\opencode_work'

doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

all_text = ""
for i, page in enumerate(doc):
    text = page.get_text()
    all_text += f"\n--- PAGE {i+1} ---\n{text}"

txt_path = os.path.join(output_dir, "mercy_house_gsa_audit_2024.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(all_text)

print(f"Extracted {len(all_text)} chars")
print(f"Saved to: {txt_path}")

# Now search for key financial data
print("\n=== KEY FINANCIAL DATA ===")
lines = all_text.split('\n')

# Look for revenue, expenses, assets, liabilities
keywords = ['revenue', 'expense', 'asset', 'liability', 'cash', 'grant', 'contract', 'compensation', 'salary', 'director', 'officer', 'ceo', 'haynes', 'deferred', 'loan', 'mortgage', 'related party']

for i, line in enumerate(lines):
    lower = line.lower()
    for kw in keywords:
        if kw in lower and len(line.strip()) > 10:
            context = lines[max(0,i-1):i+2]
            print(f"\n[P{i+1}] {line.strip()}")
            break
