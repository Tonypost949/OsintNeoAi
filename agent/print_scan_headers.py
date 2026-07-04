import os
import glob

def main():
    target_dir = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_documents"
    files = glob.glob(os.path.join(target_dir, "city*scan*.html"))
    files.extend(glob.glob(os.path.join(target_dir, "*scan*.html")))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
            
    for fpath in unique_files:
        print(f"\n========================================")
        print(f"File: {os.path.basename(fpath)}")
        print(f"========================================")
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                for _ in range(30):
                    line = f.readline()
                    if not line:
                        break
                    print(line.strip())
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
