import os

def main():
    target_files = [
        r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_files\chat-bit.html",
        r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\tablet_files\chat-bit-1.html"
    ]
    
    for fpath in target_files:
        if not os.path.exists(fpath):
            print(f"Not found: {fpath}")
            continue
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            lines = content.split('\n')
            for idx, line in enumerate(lines):
                if any(term in line.lower() for term in ["disgrace", "national", "shame", "scandal", "holes"]):
                    print(f"File: {os.path.basename(fpath)} | Line {idx+1}: {line.strip()[:150]}")
        except Exception as e:
            print(f"Error reading {fpath}: {e}")

if __name__ == "__main__":
    main()
