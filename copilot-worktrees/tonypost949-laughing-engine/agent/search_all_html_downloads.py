import os
import glob
import re

def main():
    target_dir = r"C:\Users\HP\Downloads"
    files = glob.glob(os.path.join(target_dir, "*.html"))
    
    terms = ["disgrace", "disgraced", "national", "holes", "cheese"]
    
    for fpath in files:
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            lines = content.split('\n')
            for idx, line in enumerate(lines):
                # strip html tags to see text clearly
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
