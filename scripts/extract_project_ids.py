import json
import re

with open(r'C:\OsintNeoAi\evidence\oc_procurement_portal\County_of_Orange_Procurement_Portal.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

ids = set(re.findall(r'/projects/(\d+)', text))
ids.update(re.findall(r'\"id\":\s*(\d{4,6})', text))
ids.update(re.findall(r'\"projectId\":\s*\"?(\d{4,6})\"?', text))

print(f"Total unique project IDs extracted from primary HTML: {len(ids)}")
print("Sample IDs:", sorted(list(ids))[:30])

with open(r'C:\OsintNeoAi\evidence\oc_procurement_portal\extracted_project_ids.json', 'w', encoding='utf-8') as out:
    json.dump(sorted(list(ids)), out, indent=2)
