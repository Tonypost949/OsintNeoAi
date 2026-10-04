import os
import re

def main():
    target_files = [
        r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_files\chat-bit.html",
        r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_files\chat-bit-1.html"
    ]
    
    terms = ["disgrace", "disgraced", "national", "holes", "cheese"]
    
    for fpath in target_files:
        if not os.path.exists(fpath):
            print(f"Not found: {fpath}")
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
            print(f"Error reading {fpath}: {e}")

if __name__ == "__main__":
    main()
