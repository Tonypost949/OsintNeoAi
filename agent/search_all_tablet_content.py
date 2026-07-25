import os
import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    search_dirs = [
        r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_files",
        r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_documents"
    ]
    
    terms = ["holes", "swiss cheese", "tamper", "suppress", "disgrace", "disgraced", "open", "exposed"]
    
    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        files = glob.glob(os.path.join(sdir, "*"))
        for fpath in files:
            if os.path.isdir(fpath):
                continue
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                lines = content.split('\n')
                for idx, line in enumerate(lines):
                    # Check for terms
                    for term in terms:
                        if term in line.lower():
                            # Highlight match in context
                            clean_line = re.sub('<[^<]+?>', '', line).strip()
                            if clean_line:
                                print(f"File: {os.path.basename(fpath)} | Line {idx+1} ({term}): {clean_line[:180]}")
                                break
            except Exception as e:
                pass

if __name__ == "__main__":
    main()
