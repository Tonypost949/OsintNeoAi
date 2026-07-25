import os
import re

path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\tablet_downloads\mx-report_hbpd.org_2026-06-29.txt"

if os.path.exists(path):
    print(f"File exists! Size: {os.path.getsize(path)} bytes")
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            print(f"Content length: {len(content)} characters")
            # Let's print using repr() to prevent encoding errors on windows terminal
            print("First 500 characters of file:")
            print(repr(content[:500]))
            
            # Search for national disgrace or dsigrace or disgrace
            for term in ["disgrace", "national", "dsig", "disg"]:
                matches = [m.start() for m in re.finditer(term, content, re.IGNORECASE)]
                print(f"Matches for '{term}': {len(matches)}")
                for m in matches[:10]:
                    context = content[max(0, m-100):min(len(content), m+100)].strip().replace('\n', ' ')
                    print(f"  Context: {repr(context)}")
    except Exception as e:
        print(f"Error reading file: {e}")
else:
    print("File does not exist!")
