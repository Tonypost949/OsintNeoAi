import os
import json
import re

content_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\5560\content.md"
scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

with open(content_path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's search for JSON serialized data in the js file, which contains file patches/contents
# We see entries in text like: {file:"opencode_work/index.html",patch:...} or similar.
# Actually, the OpenCodes state contains a list of files or messages.
# Let's look for any string matches for 'file:"opencode_work/' or similar.
print("Searching for file entries...")

# Let's look for "file":"opencode_work/..." or similar
file_matches = re.finditer(r'file\s*:\s*"opencode_work/([^"]+)"\s*,\s*patch\s*:\s*"([^"]+)"', text)
for m in file_matches:
    filename = m.group(1)
    patch_raw = m.group(2)
    # The patch is a string with escaped characters like \n, \t, etc.
    # Let's clean the patch to get the actual file content if it is a new file (e.g. index 0 to end)
    print(f"Found patch for: {filename}")
    
    # Unescape the patch content
    # We can do this by using json.loads to decode it as a json string
    try:
        decoded_patch = json.loads('"' + patch_raw + '"')
        # Let's see if the patch is an addition of a whole file (often starts with Index: ...)
        # Let's parse the patch. If it starts with Index:, we can extract the lines starting with + (excluding +++).
        lines = decoded_patch.split("\n")
        if len(lines) > 0 and (lines[0].startswith("Index:") or "===" in lines[1]):
            # This is a diff patch
            content_lines = []
            for line in lines:
                if line.startswith("+") and not line.startswith("+++"):
                    content_lines.append(line[1:])
                elif line.startswith(" ") or line == "":
                    content_lines.append(line[1:] if line.startswith(" ") else "")
            file_content = "\n".join(content_lines)
        else:
            file_content = decoded_patch
            
        # Write file to scratch dir
        out_file = os.path.join(scratch_dir, filename)
        with open(out_file, "w", encoding="utf-8") as out_f:
            out_f.write(file_content)
        print(f"  Successfully extracted and wrote {filename} to scratch.")
    except Exception as e:
        print(f"  Error processing patch for {filename}: {e}")

# Also search for files inside messages or other parts of the document
# Some files might be encoded differently, let's search for "Index: opencode_work/"
index_matches = re.finditer(r'Index: opencode_work/([^\s\n]+)', text)
for m in index_matches:
    print(f"Found Index match for: {m.group(1)}")
