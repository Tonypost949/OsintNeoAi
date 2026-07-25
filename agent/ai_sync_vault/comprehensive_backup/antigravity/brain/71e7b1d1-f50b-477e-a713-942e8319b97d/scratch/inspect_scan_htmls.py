import os
import re

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

files = ["bigscan.html", "cityscan.html", "cityscan2.html", "citycscan5.html"]

output_lines = []

for fn in files:
    path = os.path.join(scratch_dir, fn)
    if os.path.exists(path):
        output_lines.append(f"\n=========================================")
        output_lines.append(f"FILE: {fn} (Size: {os.path.getsize(path)} bytes)")
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        output_lines.append(f"Length: {len(content)} chars")
        output_lines.append(f"First 300 chars: {repr(content[:300])}")
        
        # Search for any occurrences of target terms
        for t in ["disgrace", "national", "dsig", "disg", "disgrace", "national disgrace"]:
            matches = list(re.finditer(t, content, re.IGNORECASE))
            if matches:
                output_lines.append(f"  -> Found {len(matches)} matches for '{t}':")
                for m in matches[:10]:
                    ctx = content[max(0, m.start()-120):min(len(content), m.end()+120)].strip().replace('\n', ' ')
                    output_lines.append(f"     Context: {repr(ctx)}")
    else:
        output_lines.append(f"File {fn} does not exist!")

# Write all output safely
out_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\scan_html_inspect_results.txt"
with open(out_path, 'w', encoding='utf-8') as out_f:
    for line in output_lines:
        out_f.write(line + "\n")

# Safe console print
print(f"Results written to {out_path}.")
with open(out_path, 'r', encoding='utf-8') as f:
    text = f.read()
    print(text.encode('ascii', 'backslashreplace').decode('ascii'))
