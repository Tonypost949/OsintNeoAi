import csv
import os

# Search Gmail index for Brad Smith
print('=== GMAIL INDEX SEARCH ===\n')
gmail_path = r'C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_gmail_index.csv'
try:
    with open(gmail_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_text = ' '.join([str(v) for v in row.values() if v]).upper()
            if 'BRAD SMITH' in row_text or 'SGT SMITH' in row_text or 'SMITH, BRAD' in row_text:
                print(f"Subject: {row.get('subject', '')}")
                print(f"From: {row.get('sender', '')}")
                print(f"Date: {row.get('date_header', '')}")
                print(f"Snippet: {row.get('snippet', '')[:200]}")
                print()
except Exception as e:
    print(f'Error: {e}')

# Search extracted text files
print('\n=== EXTRACTED TEXT SEARCH ===\n')
extracted_dir = r'C:\Users\HP\OneDrive\Documents\opencode_work\extracted_text'
if os.path.exists(extracted_dir):
    for filename in os.listdir(extracted_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(extracted_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().upper()
                    if 'BRAD SMITH' in content or 'SGT SMITH' in content:
                        print(f'Found in: {filename}')
                        # Find context around the mention
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'BRAD SMITH' in line or 'SGT SMITH' in line:
                                start = max(0, i-2)
                                end = min(len(lines), i+3)
                                print('Context:')
                                for j in range(start, end):
                                    print(f'  {lines[j]}')
                                print()
            except Exception as e:
                pass

# Search OCR output
print('\n=== OCR OUTPUT SEARCH ===\n')
ocr_dir = r'C:\Users\HP\OneDrive\Documents\opencode_work\ocr_output'
if os.path.exists(ocr_dir):
    for filename in os.listdir(ocr_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(ocr_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().upper()
                    if 'BRAD SMITH' in content or 'SGT SMITH' in content:
                        print(f'Found in: {filename}')
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'BRAD SMITH' in line or 'SGT SMITH' in line:
                                start = max(0, i-2)
                                end = min(len(lines), i+3)
                                print('Context:')
                                for j in range(start, end):
                                    print(f'  {lines[j]}')
                                print()
            except Exception as e:
                pass

print('Search complete.')
