import json

for name, file in [('EVIDENCE', 'inventory_evidence.json'), ('DOWNLOADS', 'inventory_downloads.json')]:
    with open('C:/OsintNeoAi/.agents/explorer_survey_1/' + file, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(f"=== {name} SUMMARY ===")
    print(f"Base path: {d['base_path']}")
    print(f"Total files: {d['total_files']}, Total size: {d['total_size_bytes'] / (1024*1024):.2f} MB")
    print(f"Top subdirs ({len(d['subdirs'])} total): {d['subdirs'][:15]}")
    sorted_exts = sorted(d['extensions'].items(), key=lambda x: x[1]['count'], reverse=True)
    print("Extensions breakdown:")
    for ext, data in sorted_exts[:20]:
        print(f"  {ext:15}: count={data['count']:5}, size={data['total_bytes']/(1024*1024):8.2f} MB")
    print()
