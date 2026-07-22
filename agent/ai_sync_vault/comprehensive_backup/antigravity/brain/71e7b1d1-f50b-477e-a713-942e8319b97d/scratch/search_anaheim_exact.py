import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
txt_path = os.path.join(scratch_dir, "anaheim_details.txt")
out_path = os.path.join(scratch_dir, "exact_address_matches.txt")

if not os.path.exists(txt_path):
    print("Anaheim details file does not exist!")
    os._exit(1)

with open(txt_path, 'r', encoding='utf-8') as f:
    text = f.read()

import re
blocks = re.split(r'--------------------------------------------------------------------------------', text)

targets = ["213 N. Gilbert", "632 N. East", "Covenant House California", "Covenant House", "Gilbert St", "East St"]

matches_found = []

for b in blocks:
    b_lower = b.lower()
    found_targets = [t for t in targets if t.lower() in b_lower]
    if found_targets:
        matches_found.append((b, found_targets))

with open(out_path, 'w', encoding='utf-8') as out_f:
    out_f.write(f"EXACT ADDRESS AND COVENANT HOUSE MATCHES FROM DEEPSEEK EXPORTS\n")
    out_f.write(f"===============================================================\n\n")
    
    out_f.write(f"Total matching blocks found: {len(matches_found)}\n\n")
    
    for i, (b, t_list) in enumerate(matches_found):
        out_f.write(f"========================================================================\n")
        out_f.write(f"BLOCK #{i+1} | MATCHED SUBSTRINGS: {t_list}\n")
        out_f.write(f"========================================================================\n")
        out_f.write(b.strip() + "\n\n")

print(f"Wrote {len(matches_found)} exact matches to {out_path}.")
for idx, (b, t_list) in enumerate(matches_found):
    lines = b.strip().split('\n')
    header = lines[0] if lines else "Untitled"
    print(f"Match #{idx+1}: {header} (Matched: {t_list})")
