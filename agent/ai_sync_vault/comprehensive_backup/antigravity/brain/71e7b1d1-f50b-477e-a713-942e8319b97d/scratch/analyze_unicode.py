import re

html_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\855\content.md"

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Let's find unicode escape sequences like \u4e00 through \u9fff
unicode_escapes = re.findall(r'\\u([0-9a-fA-F]{4})', content)
print(f"Found {len(unicode_escapes)} unicode escape sequences.")

# Let's see if we can decode them and find Chinese characters
decoded_chars = []
for h in unicode_escapes:
    try:
        char = chr(int(h, 16))
        decoded_chars.append(char)
    except:
        pass

decoded_string = "".join(decoded_chars)
chinese_only = [c for c in decoded_chars if '\u4e00' <= c <= '\u9fff']
print(f"Decoded characters length: {len(decoded_chars)}")
print(f"Chinese decoded characters: {len(chinese_only)}")
if chinese_only:
    print(f"Sample decoded Chinese characters: {''.join(chinese_only[:100])}")

# Let's search for patterns like:
# ["id", "name", ...] or similar.
# In Google Drive INITIAL_DATA, it's a huge nested array of lists.
# Let's search for any occurrence of drive file IDs or links.
# Let's see what is inside content.md
# Google Drive files often look like:
# "1...-..." (length of 33) or containing specific extensions.
# Let's look for common files by looking at lines in content.md containing '\\u'
unicode_lines = []
for line in content.splitlines():
    if '\\u' in line:
        unicode_lines.append(line)

print(f"Found {len(unicode_lines)} lines containing '\\u'")
if unicode_lines:
    print("Example lines with unicode escapes (first 2):")
    for ul in unicode_lines[:2]:
        print(ul[:300])
