import re, sys, os

INPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local_scan_extracted_text.csv")
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local_scan_extracted_text_clean.csv")

SECRET_PATTERNS = [
    r'AIza[0-9A-Za-z_-]{35}',
    r'client_secret["\s:=]+[A-Za-z0-9_-]{24,}',
    r'"client_secret"\s*:\s*"[^"]+"',
    r'"client_id"\s*:\s*"[0-9]+-[a-z0-9]+\.apps\.googleusercontent\.com"',
    r'GCP.*key.*AIza',
    r'OAuth.*secret.*[A-Za-z0-9_-]{20,}',
    r'"type"\s*:\s*"service_account"',
    r'"private_key"\s*:',
    r'-----BEGIN (RSA )?PRIVATE KEY-----',
    r'ya29\.[0-9A-Za-z_-]+',
]

with open(INPUT, "r", encoding="utf-8-sig", errors="replace") as f:
    lines = f.readlines()

cleaned = []
dirty = 0
for line in lines:
    found = False
    for pat in SECRET_PATTERNS:
        if re.search(pat, line, re.IGNORECASE):
            found = True
            break
    if found:
        dirty += 1
        cleaned.append("[REDACTED - SECRET REMOVED]\n")
    else:
        cleaned.append(line.rstrip() + "\n")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.writelines(cleaned)

print(f"Input lines: {len(lines)}")
print(f"Output lines: {len(cleaned)}")
print(f"Secrets removed: {dirty}")
print(f"Output: {OUTPUT}")
