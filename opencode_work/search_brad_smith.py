import csv

# Search all CSVs for Brad Smith references
search_terms = ['BRAD SMITH', 'SGT SMITH', 'SMITH, BRAD', 'BRADLEY SMITH']

files_to_search = [
    r'C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_gmail_index.csv',
    r'C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_drive_file_index.csv',
    r'C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_evidence_chain_of_custody.csv',
    r'C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_all_state_records.csv',
    r'C:\Users\HP\OneDrive\Documents\opencode_work\mat_looker_forensic_base.csv',
]

print('=== SEARCHING FOR SGT BRAD SMITH ===\n')

for filepath in files_to_search:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_text = ' '.join([str(v) for v in row.values() if v]).upper()
                for term in search_terms:
                    if term in row_text:
                        print(f'FOUND in {filepath.split("\\")[-1]}:')
                        for key, value in row.items():
                            if value:
                                print(f'  {key}: {value[:200]}')
                        print()
                        break
    except Exception as e:
        print(f'Error reading {filepath}: {e}')

print('Search complete.')
