import json
import os
import re
import csv

out_of_state_keywords = {
    'NJ': ['New Jersey', 'Hamilton', 'Ewing', 'Trenton', 'Mercer County', 'Helene Fuld', 'Cedar Lane', '08610', '08619', '08628', '08638', '08620', '3:20-mj-05007', 'Zartman', 'Innocenzi'],
    'NV': ['Nevada', 'Las Vegas', 'Clark County', 'BROWN HUBERT', 'Casutt', '2:21-cr-00215', 'Beyond Nevada'],
    'DE': ['Delaware', 'Wilmington', 'DE LLC', 'DE Corporation', 'Delaware Layer'],
    'TX': ['Texas', 'Houston', 'Harris County', 'Westheimer', 'Amir Aqeel', '4:20-cr-00567', 'drillingoilandgas'],
    'FL': ['Florida', 'Greenacres', 'Palm Beach', 'Lake Pine Circle', 'David T. Hines', '1:20-mj-03183', 'Brickell', "Dog's Day Productions", '33463'],
    'WA': ['Washington', 'Seattle', 'King County', 'Spokane'],
    'AZ': ['Arizona', 'Phoenix', 'Tucson', 'Scottsdale', 'Willie Mitchell', '2:21-cr-00812', 'Camelback'],
    'CT': ['Connecticut', 'Waterbury', 'Post University', 'post.edu', '06708'],
    'NY': ['New York', 'Manhattan', 'Wall St', 'Rafael Ferguson', 'T3 Trading'],
    'GA': ['Georgia', 'Atlanta', 'Mark Dawkins', '1:21-cr-00312', 'Peachtree'],
    'PA': ['Pennsylvania', 'Philadelphia', 'Chadds Ford', 'PHL']
}

results = {st: [] for st in out_of_state_keywords}

def scan_text(text, source_name):
    for st, kws in out_of_state_keywords.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE):
                results[st].append({'keyword': kw, 'source': source_name})
                break

# 1. Scan master registry JSON / CSV files in data/ and master_osint_sheet/
target_files = [
    r'C:\OsintNeoAi\data\MASTER_OSINT_EVIDENCE_REGISTRY.json',
    r'C:\OsintNeoAi\data\leads_feed.json',
    r'C:\OsintNeoAi\data\nationwide_ppp_loan_fraud_enterprise_correlation.json',
    r'C:\OsintNeoAi\data\nationwide_counterfeit_prescription_correlation.json',
    r'C:\OsintNeoAi\master_osint_sheet\master_osint_registry.json',
    r'C:\OsintNeoAi\forensic\deliverables\Unified_Export.json',
    r'C:\OsintNeoAi\evidence\FORENSIC_CORRELATION_MATRIX.json'
]

for tf in target_files:
    if os.path.exists(tf):
        print(f'Scanning {tf}...')
        try:
            with open(tf, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            scan_text(content, os.path.basename(tf))
        except Exception as e:
            print(f'Error reading {tf}: {e}')

# 2. Scan briefings/
briefings_dir = r'C:\OsintNeoAi\briefings'
if os.path.exists(briefings_dir):
    for fn in os.listdir(briefings_dir):
        if fn.endswith('.md'):
            fp = os.path.join(briefings_dir, fn)
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                scan_text(f.read(), f'briefings/{fn}')

# 3. Scan filtered chats
chats_dir = r'C:\OsintNeoAi\data\filtered_chats'
if os.path.exists(chats_dir):
    for fn in os.listdir(chats_dir):
        if fn.endswith('.txt'):
            fp = os.path.join(chats_dir, fn)
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                scan_text(f.read(), f'filtered_chats/{fn}')

print('=== SUMMARY OF OUT-OF-STATE FINDINGS ===')
for st, hits in results.items():
    sources = set(h['source'] for h in hits)
    kws = set(h['keyword'] for h in hits)
    print(f'State: {st} | Total Hits: {len(hits)} | Unique Sources: {len(sources)} | Matched KWs: {list(kws)}')
    for s in list(sources)[:5]:
        print(f'   - {s}')
