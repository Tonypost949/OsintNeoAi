import os
import re

path = r"C:\Users\HP\Downloads\Dehashed HBPD scan - DeepSeek_files\saved_resource.html"

if os.path.exists(path):
    print(f"File exists! Size: {os.path.getsize(path)} bytes")
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            print(f"Content length: {len(content)} chars")
            
            # Let's search for disgrace, dsigrace, disg, dsig, national
            for term in ["disgrace", "national", "dsig", "disg", "national disgrace", "dsigrace"]:
                matches = list(re.finditer(term, content, re.IGNORECASE))
                print(f"Matches for '{term}': {len(matches)}")
                for m in matches[:10]:
                    ctx = content[max(0, m.start()-120):min(len(content), m.end()+120)].strip().replace('\n', ' ')
                    print(f"  Context: {repr(ctx)}")
    except Exception as e:
        print(f"Error reading file: {e}")
else:
    print("File does not exist!")
