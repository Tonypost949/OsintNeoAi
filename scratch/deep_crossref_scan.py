import csv
import glob
import os
import re

search_dirs = [
    r"C:\OsintNeoAi\evidence",
    r"C:\OsintNeoAi\workspaces\riconow\opencode_work",
    r"C:\OsintNeoAi\agent"
]

jpm_count = 0
harvest_count = 0
jpm_maricopa = []
harvest_maricopa = []

pattern_jpm = re.compile(r"JPMorgan Chase Bank", re.IGNORECASE)
pattern_harvest = re.compile(r"Harvest Small Business Finance", re.IGNORECASE)
pattern_maricopa = re.compile(r"Maricopa", re.IGNORECASE)

print("Scanning for intersections...")

for d in search_dirs:
    for root, dirs, files in os.walk(d):
        for file in files:
            if file.endswith('.csv'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            has_jpm = bool(pattern_jpm.search(line))
                            has_harvest = bool(pattern_harvest.search(line))
                            has_maricopa = bool(pattern_maricopa.search(line))
                            
                            if has_jpm: jpm_count += 1
                            if has_harvest: harvest_count += 1
                            
                            if has_jpm and has_maricopa:
                                jpm_maricopa.append(f"{file}:{line_num} -> {line[:200]}")
                            if has_harvest and has_maricopa:
                                harvest_maricopa.append(f"{file}:{line_num} -> {line[:200]}")
                except Exception as e:
                    pass

print(f"JPMorgan total hits: {jpm_count}")
print(f"Harvest total hits: {harvest_count}")

print(f"\n--- JPMorgan + Maricopa Overlaps ({len(jpm_maricopa)}) ---")
for x in jpm_maricopa[:10]:
    print(x.strip())

print(f"\n--- Harvest + Maricopa Overlaps ({len(harvest_maricopa)}) ---")
for x in harvest_maricopa[:10]:
    print(x.strip())
