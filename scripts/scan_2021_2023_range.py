import os
import datetime
import json
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
start_ts = datetime.datetime(2021, 1, 1).timestamp()
end_ts = datetime.datetime(2023, 3, 31, 23, 59, 59).timestamp()

date_files = []
for f in root.glob('**/*.*'):
    if f.is_file():
        path_str = str(f)
        if 'opencode_work' in path_str or 'copilot-worktrees' in path_str or '.git' in path_str or 'archive' in path_str:
            continue
        try:
            mtime = f.stat().st_mtime
            if start_ts <= mtime <= end_ts:
                dt_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                date_files.append({
                    'date': dt_str,
                    'file': f.name,
                    'path': str(f),
                    'size_kb': round(f.stat().st_size / 1024, 1)
                })
        except Exception:
            pass

date_files.sort(key=lambda x: x['date'])

out_file = root / 'data' / 'jan2021_march2023_all_files.json'
out_file.write_text(json.dumps(date_files, indent=2), encoding='utf-8')

print(f"TOTAL FILES FOUND FROM JAN 2021 TO MARCH 2023: {len(date_files)}")
print("\nEarliest files in range:")
for d in date_files[:20]:
    print(f" - [{d['date']}] {d['file']} ({d['size_kb']} KB)")
