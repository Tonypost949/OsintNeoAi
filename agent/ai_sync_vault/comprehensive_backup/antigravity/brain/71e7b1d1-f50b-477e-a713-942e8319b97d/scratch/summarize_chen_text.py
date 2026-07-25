import re

filepath = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\chen_extracted_text.txt"

chinese_char_re = re.compile(r"[\u4e00-\u9fff]")

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

pages = content.split("================ PAGE ")

print(f"Total parsed pages: {len(pages)-1}")

print("\n--- FINDING CHINESE CHARACTERS & TRANSNATIONAL DETAILS ---")
found_pages = []
for p in pages[1:]:
    lines = p.split('\n')
    page_num = lines[0].split(" ================")[0].strip()
    page_text = '\n'.join(lines[1:])
    
    matches = chinese_char_re.findall(page_text)
    if matches:
        found_pages.append((page_num, len(matches), page_text))

print(f"Found {len(found_pages)} pages with Chinese characters.")
for num, count, text in found_pages:
    print(f"\nPAGE {num} ({count} Chinese characters):")
    # print the lines that contain Chinese
    for line in text.split('\n'):
        if chinese_char_re.search(line):
            print(f"  [CN_LINE] {line.strip()}")

print("\n--- KEY OSINT SECTIONS & HEADINGS ---")
# Print lines that look like section headers or have money amounts
for line in content.split('\n')[:200]:
    if line.strip() and (line.startswith("I.") or line.startswith("II.") or line.startswith("III.") or line.startswith("IV.") or line.startswith("V.") or "Exhibit" in line or "EXHIBIT" in line):
        print(line.strip())
