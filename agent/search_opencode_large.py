import os

def main():
    target_path = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\opencode_data_nofIV75K.txt"
    if not os.path.exists(target_path):
        print("File not found")
        return
        
    print("Searching opencode_data_nofIV75K.txt...")
    with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    lines = content.split('\n')
    for idx, line in enumerate(lines):
        if "holes" in line.lower() or "disgrace" in line.lower() or "other states" in line.lower():
            print(f"Line {idx+1}: {line.strip()[:180]}")

if __name__ == "__main__":
    main()
