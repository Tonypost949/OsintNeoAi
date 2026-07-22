import re
import json

html_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\855\content.md"

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Let's extract all script blocks
scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
print(f"Found {len(scripts)} script blocks.")

# Let's write them to a file so we can search them
with open("all_scripts.js", "w", encoding='utf-8') as f:
    for i, script in enumerate(scripts):
        f.write(f"// --- SCRIPT {i} ---\n")
        f.write(script)
        f.write("\n\n")

print("Wrote all script blocks to all_scripts.js")

# Let's search all_scripts.js for some common file extensions, Chinese characters, or interesting variables
# Check if there is "window._INITIAL_DATA" or similar in content
for var_name in ["_INITIAL_DATA", "bootstrap", "boot_data", "drive_web", "FILE_LIST", "folder"]:
    matches = [m for m in scripts if var_name in m]
    if matches:
        print(f"Variable '{var_name}' found in {len(matches)} script blocks.")

# Let's search for Chinese characters in scripts
chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]')
chinese_matches = chinese_char_pattern.findall(content)
print(f"Found {len(chinese_matches)} Chinese characters in the entire HTML file.")

# Let's write a regex search for Chinese characters along with some surrounding context
chinese_lines = []
for line in content.splitlines():
    if chinese_char_pattern.search(line):
        chinese_lines.append(line)
print(f"Found {len(chinese_lines)} lines containing Chinese characters.")
if chinese_lines:
    print("Example lines with Chinese characters:")
    for line in chinese_lines[:5]:
        print(line[:200])
