import os
import re

downloads_dir = r"C:\Users\HP\Downloads"

print(f"Scanning root files in {downloads_dir} safely...")

target_terms = ["disgrace", "national", "dsig", "disg", "dsigrace"]

output_lines = []

for f in os.listdir(downloads_dir):
    fp = os.path.join(downloads_dir, f)
    if os.path.isfile(fp) and f.endswith(('.html', '.txt', '.md', '.json', '.xml', '.csv')):
        f_safe = f.encode('ascii', 'backslashreplace').decode('ascii')
        try:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
                content = file_obj.read()
                found = False
                for term in target_terms:
                    matches = list(re.finditer(term, content, re.IGNORECASE))
                    if matches:
                        if not found:
                            output_lines.append(f"\n=========================================")
                            output_lines.append(f"FILE: {f_safe}")
                            found = True
                        output_lines.append(f"  -> Found {len(matches)} matches for '{term}':")
                        for m in matches[:10]:
                            ctx = content[max(0, m.start()-120):min(len(content), m.end()+120)].strip().replace('\n', ' ')
                            ctx_safe = ctx.encode('ascii', 'backslashreplace').decode('ascii')
                            output_lines.append(f"     Context: {repr(ctx_safe)}")
        except Exception as e:
            output_lines.append(f"Error reading {f_safe}: {str(e)}")

# Write safely
out_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\scan_downloads_root_results.txt"
with open(out_path, 'w', encoding='utf-8') as out_f:
    for line in output_lines:
        out_f.write(line + "\n")

print(f"Done. Saved to {out_path}.")
# Print lines from out_path containing 'disgrace' or 'dsigrace' or 'disg' (ignoring Android signature .idsig)
print("\n--- CRITICAL MATCHES (disgrace / dsigrace) ---")
with open(out_path, 'r', encoding='utf-8') as f:
    for line in f:
        # Ignore our scripts, result files, and standard signature extensions .idsig
        if any(x in line for x in ["idsig", "all_state_records", "disguise"]):
            continue
        if "disgrace" in line.lower() or "dsigrace" in line.lower() or "dsig" in line.lower() or "disg" in line.lower():
            print(line.strip())
