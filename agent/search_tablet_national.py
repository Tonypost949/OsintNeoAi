import os
import glob
import sys

# Ensure stdout uses utf-8 encoding to prevent charmap print errors
sys.stdout.reconfigure(encoding='utf-8')

def main():
    target_dir = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_files"
    files = glob.glob(os.path.join(target_dir, "*"))
    
    for fpath in files:
        if os.path.isdir(fpath):
            continue
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            lines = content.split('\n')
            for idx, line in enumerate(lines):
                if "national" in line.lower():
                    print(f"File: {os.path.basename(fpath)} | Line {idx+1}: {line.strip()}")
        except Exception as e:
            print(f"Error reading {fpath}: {e}")

if __name__ == "__main__":
    main()
