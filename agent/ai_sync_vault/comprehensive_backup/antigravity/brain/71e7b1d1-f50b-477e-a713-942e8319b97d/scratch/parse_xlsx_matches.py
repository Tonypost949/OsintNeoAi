import os

log_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\tasks\task-4496.log"
output_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\xlsx_matches_summary.txt"

if not os.path.exists(log_path):
    print("Log file does not exist yet.")
    exit(1)

xlsx_matches = []
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if line.startswith("[XLSX]"):
            xlsx_matches.append(line.strip())

print(f"Found {len(xlsx_matches)} XLSX matches in the log.")
with open(output_path, "w", encoding="utf-8") as out:
    for match in xlsx_matches:
        out.write(match + "\n")
        print(match[:200])

print("Finished! Matches saved to:", output_path)
