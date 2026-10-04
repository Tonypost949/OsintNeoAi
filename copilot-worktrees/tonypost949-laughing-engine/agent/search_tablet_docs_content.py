import os
import glob
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def main():
    target_dir = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_documents"
    files = glob.glob(os.path.join(target_dir, "*"))
    
    terms = ["disgrace", "national", "holes", "shame"]
    
    for fpath in files:
        if os.path.isdir(fpath):
            continue
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            lines = content.split('\n')
            for idx, line in enumerate(lines):
                clean_line = re.sub('<[^<]+?>', '', line).strip()
                if not clean_line:
                    continue
                for term in terms:
                    if term in clean_line.lower():
                        print(f"File: {os.path.basename(fpath)} | Line {idx+1} ({term}): {clean_line[:180]}")
                        break
        except Exception as e:
            # Skip binary files if they fail to read cleanly, but xlsx usually has XML files zipped
            pass

if __name__ == "__main__":
    main()
