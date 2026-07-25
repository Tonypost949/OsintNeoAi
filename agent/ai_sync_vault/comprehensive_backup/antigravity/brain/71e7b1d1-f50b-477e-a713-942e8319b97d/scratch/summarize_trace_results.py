import json
import os

path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\master_trace_results.json"
out_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\summary_of_findings.txt"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(out_path, "w", encoding="utf-8") as out:
    out.write(f"KEYS in master_trace_results.json: {list(data.keys())}\n")
    
    for key, val in data.items():
        out.write(f"\n==================== {key} ({len(val)} items) ====================\n")
        for idx, item in enumerate(val):
            out.write(f"[{idx+1}]\n")
            for k, v in item.items():
                out.write(f"  {k}: {v}\n")

print("Successfully wrote summary to:", out_path)
