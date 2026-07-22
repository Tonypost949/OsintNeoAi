import os
import re

content_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\5560\content.md"
scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

with open(content_path, "r", encoding="utf-8") as f:
    text = f.read()

def manual_unescape(s):
    res = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '\\':
            if i + 1 < n:
                next_c = s[i+1]
                if next_c == 'n':
                    res.append('\n')
                    i += 2
                elif next_c == 't':
                    res.append('\t')
                    i += 2
                elif next_c == 'r':
                    res.append('\r')
                    i += 2
                elif next_c == '"':
                    res.append('"')
                    i += 2
                elif next_c == "'":
                    res.append("'")
                    i += 2
                elif next_c == '\\':
                    res.append('\\')
                    i += 2
                elif next_c == '/':
                    res.append('/')
                    i += 2
                elif next_c == 'b':
                    res.append('\b')
                    i += 2
                elif next_c == 'f':
                    res.append('\f')
                    i += 2
                elif next_c == 'x':
                    if i + 3 < n:
                        hex_code = s[i+2:i+4]
                        res.append(chr(int(hex_code, 16)))
                        i += 4
                    else:
                        res.append('\\x')
                        i += 2
                elif next_c == 'u':
                    if i + 5 < n:
                        hex_code = s[i+2:i+6]
                        res.append(chr(int(hex_code, 16)))
                        i += 6
                    else:
                        res.append('\\u')
                        i += 2
                else:
                    res.append(next_c)
                    i += 2
            else:
                res.append('\\')
                i += 1
        else:
            res.append(c)
            i += 1
    return "".join(res)

# Regex to match double-quoted string with backslash escapes
# Pattern: "([^"\\]*(?:\\.[^"\\]*)*)"
# We search for file : "opencode_work/..." and then patch : "..."
pattern = r'file\s*:\s*"opencode_work/([^"]+)"\s*,\s*patch\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"'
matches = list(re.finditer(pattern, text))
print(f"Found {len(matches)} total file-patch matches in content.md.")

# We will group by file name and track the files.
# For each file, we will apply the patches in chronological order (order of appearance in the file).
files_db = {}

def apply_patch(current_content, patch_text):
    # If the patch is not a diff (doesn't start with Index:), it is the full file content
    if not patch_text.startswith("Index:"):
        return patch_text
    
    # It is a unified diff. Let's parse it.
    lines = patch_text.split("\n")
    if len(lines) < 4:
        return patch_text
    
    # Let's check if it is a new file addition (starts with --- /dev/null or index 0,0)
    # Actually, let's look for @@ -0,0 ...
    is_new = False
    for line in lines[:10]:
        if "--- /dev/null" in line or "--- opencode_work" in line and "+++ opencode_work" in line:
            # Check if we have @@ -0,0
            pass
    # Let's check if the current content is empty. If so, or if we want to be safe:
    # A simple patcher for adding files:
    # If the file is a new addition, all of its lines start with '+'
    # Let's inspect the hunk headers.
    # If we are patching, let's write a simple patch algorithm or reconstruct if it's mostly additions.
    # Let's implement a robust unified diff patcher!
    current_lines = current_content.split("\n") if current_content else []
    new_lines = []
    
    # We parse the diff line by line
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("Index:") or line.startswith("===") or line.startswith("---") or line.startswith("+++"):
            i += 1
            continue
        elif line.startswith("@@"):
            # Hunk header: @@ -start,len +start,len @@
            m = re.match(r'@@\s*-(\d+),?(\d*)\s*\+(\d+),?(\d*)\s*@@', line)
            if not m:
                i += 1
                continue
            old_start = int(m.group(1))
            old_len = int(m.group(2)) if m.group(2) else 1
            new_start = int(m.group(3))
            new_len = int(m.group(4)) if m.group(4) else 1
            
            # If old_start is 0, it means it's a new file
            if old_start == 0:
                # All lines in the hunk starting with '+' should be added
                i += 1
                while i < len(lines) and not lines[i].startswith("@@"):
                    l = lines[i]
                    if l.startswith("+"):
                        new_lines.append(l[1:])
                    i += 1
                continue
            
            # For existing files, let's match the old lines and apply edits.
            # However, if we look at the files, almost all of them are added as new files in opencode,
            # or the patches are complete replacements (since the agent wrote them from scratch).
            # Let's see: if the patch contains only additions (+), we can just reconstruct it by taking all lines starting with '+'.
            # Let's check if there are deletion lines.
            has_deletions = any(l.startswith("-") and not l.startswith("---") for l in lines)
            if not has_deletions:
                # Reconstruct directly by taking all '+' lines (excluding +++)
                reconstructed = []
                for l in lines:
                    if l.startswith("+") and not l.startswith("+++"):
                        reconstructed.append(l[1:])
                    elif l.startswith(" ") or l == "":
                        reconstructed.append(l[1:] if l.startswith(" ") else "")
                return "\n".join(reconstructed)
            
            # If there are deletions, let's do a simple patch.
            # For simplicity, if a file has deletions, let's print a message.
            # Let's write a standard patch application.
            # To do a real patch, we trace through the old lines and apply additions/deletions.
            # Let's write a simple patch applicator:
            # We align with current_lines and replace chunks.
            # A standard diff has old lines starting with ' ' or '-', and new lines starting with ' ' or '+'.
            hunk_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("@@"):
                hunk_lines.append(lines[i])
                i += 1
            
            # Let's apply this hunk to current_lines
            # We find the matching block in current_lines starting near old_start
            # Since line numbers are 1-based, index is old_start - 1
            idx = old_start - 1
            # We replace old_len lines starting at idx with the new lines from the hunk
            replacement = []
            for hl in hunk_lines:
                if hl.startswith("+"):
                    replacement.append(hl[1:])
                elif hl.startswith(" "):
                    replacement.append(hl[1:])
                elif hl.startswith("-"):
                    # skip deleted line
                    pass
            
            # Update current_lines
            current_lines[idx:idx+old_len] = replacement
            # Continue to next lines
            continue
        else:
            i += 1
            
    if current_lines:
        return "\n".join(current_lines)
    return "\n".join(new_lines)

for idx, m in enumerate(matches):
    filename = m.group(1)
    patch_escaped = m.group(2)
    patch_text = manual_unescape(patch_escaped)
    
    print(f"[{idx+1}] File: {filename}, Patch length: {len(patch_text)}")
    
    current_content = files_db.get(filename, "")
    new_content = apply_patch(current_content, patch_text)
    files_db[filename] = new_content

# Write all extracted files to scratch dir
for filename, content in files_db.items():
    out_file = os.path.join(scratch_dir, filename)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Extracted and wrote: {filename} ({len(content)} characters)")
