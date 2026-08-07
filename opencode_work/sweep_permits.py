import os

manifest_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\permit_backups_manifest.txt"
targets = ["17642 Beach", "17631 Cameron"]
matches = []

print("=== Starting Targeted Permit Sweep ===")

if not os.path.exists(manifest_path):
    print(f"Manifest not found at: {manifest_path}")
    exit(1)

with open(manifest_path, "r", encoding="utf-8", errors="ignore") as f:
    files = [line.strip() for line in f if line.strip()]

print(f"Scanning {len(files)} files for targets: {targets}...\n")

for file_path in files:
    if not os.path.exists(file_path) or not file_path.lower().endswith('.pdf'):
        continue

    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue

            for target in targets:
                if target.lower() in text.lower():
                    hit = f"Match found in [{file_path}] on Page {page_num + 1} for '{target}'"
                    print(f"HIT: {hit}")
                    matches.append(hit)
    except Exception as e:
        continue

print("\n=== Sweep Complete ===")
print(f"Total target matches flagged: {len(matches)}")

output_log = r"C:\Users\HP\OneDrive\Documents\opencode_work\permit_search_hits.txt"
with open(output_log, "w", encoding="utf-8") as out:
    out.write("\n".join(matches))
print(f"Results saved to {output_log}")
