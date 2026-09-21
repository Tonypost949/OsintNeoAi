import os
import json

TARGET_DIR = r"C:\Users\Amd949609\Downloads"
KEYWORDS = ["stormtech", "corrosion", "wrapped", "wrap", "permit", "blueprint", "hbnc", "17641", "17631", "17642", "yamada", "plumbing", "chromium", "hexavalent", "w-4150", "20ic002"]

matches = []

for root, dirs, files in os.walk(TARGET_DIR):
    for f in files:
        if f.lower().endswith((".json", ".html", ".htm", ".txt", ".md", ".csv")):
            file_path = os.path.join(root, f)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
                    content_lower = content.lower()
                    
                    found_kw = [kw for kw in KEYWORDS if kw in content_lower]
                    if "stormtech" in content_lower or "wrapped" in content_lower or "corrosion" in content_lower:
                        matches.append({
                            "filename": f,
                            "path": file_path,
                            "keywords_found": found_kw,
                            "excerpt": content[:300].replace("\n", " ")
                        })
            except Exception as e:
                pass

print(f"Total specific matches found for StormTech/Corrosion/Permits: {len(matches)}")
for m in matches:
    print(f"\n[+] File: {m['filename']}")
    print(f"    Path: {m['path']}")
    print(f"    Keywords: {m['keywords_found']}")

with open(r"C:\OsintNeoAi\evidence\hbnc_stormtech_corrosion_matches.json", "w", encoding="utf-8") as out:
    json.dump(matches, out, indent=2)
