import re

with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\geotracker\permitted_ust.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    parts = line.split('\t')
    if len(parts) >= 3:
        # Remove all quotes from business name (field index 2)
        parts[2] = parts[2].replace('"', '').replace("'", "'")
    fixed_lines.append('\t'.join(parts))

with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\geotracker\permitted_ust_clean.txt', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('Fixed', len(fixed_lines), 'lines')
