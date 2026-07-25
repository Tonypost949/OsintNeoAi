import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
txt_path = os.path.join(scratch_dir, "anaheim_details.txt")

if not os.path.exists(txt_path):
    print("Anaheim details file does not exist!")
    os._exit(1)

with open(txt_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search for matches and print sections
# Let's write out all paragraphs that contain "gilbert", "east st" or "covenant" to a clean summary file.
import re

matches = re.split(r'--------------------------------------------------------------------------------', text)
print(f"Total MATCH blocks: {len(matches)}")

print("\n=== ANAHEIM ADDRESS MATCHES IN DEEPSEEK EXPORTS ===")

count = 0
for m in matches:
    if not m.strip():
        continue
    m_lower = m.lower()
    if "gilbert" in m_lower or "east" in m_lower or "covenant" in m_lower:
        # Check if it mentions Anaheim or specific addresses
        print("\n--- MATCH BLOCK ---")
        lines = m.strip().split('\n')
        header = lines[0] if lines else ""
        header_safe = header.encode('ascii', 'backslashreplace').decode('ascii')
        print(f"Block info: {header_safe}")
        
        # Print lines containing interest words with context
        for i, line in enumerate(lines):
            if any(w in line.lower() for w in ["gilbert", "east", "covenant"]):
                start = max(0, i - 2)
                end = min(len(lines), i + 8)
                print(f"  [Line {i+1} Match]:")
                for j in range(start, end):
                    prefix = "  >>> " if j == i else "      "
                    line_safe = lines[j].encode('ascii', 'backslashreplace').decode('ascii')
                    print(f"{prefix}{line_safe}")
                print("  " + "."*30)
        count += 1

print(f"\nTotal matches with keywords: {count}")
