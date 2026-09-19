import json

path = r'C:\OsintNeoAi\data\master_accounts_crossref_matches.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for acc in ['anthony.dimarcello@students.post.edu', 'ironmandavinci@gmail.com']:
    print(f'=== {acc} ===')
    matches = data.get('full_matches', {}).get(acc, [])
    print(f'Count: {len(matches)}')
    for m in matches:
        ds = m.get('dataset')
        p = m.get('relative_path')
        fn = m.get('filename')
        sha = m.get('sha256', '')[:16]
        print(f'  Dataset: {ds} | File: {fn} | Path: {p}')
