import os
import glob
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    target_dir = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_documents"
    files = glob.glob(os.path.join(target_dir, "city*.html"))
    files.append(os.path.join(target_dir, "untitled.html"))
    
    for fpath in files:
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            lines = content.split('\n')
            for idx, line in enumerate(lines):
                if "citydomains" in line.lower() or "const citydomains" in line.lower():
                    print(f"\nFile: {os.path.basename(fpath)} | Line {idx+1}")
                    for k in range(idx, min(len(lines), idx + 15)):
                        print(f"Line {k+1}: {lines[k].strip()}")
                    break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
