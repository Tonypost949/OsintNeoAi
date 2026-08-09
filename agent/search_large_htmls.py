import os

def main():
    target_files = [
        r"C:\Users\HP\Downloads\Dehashed HBPD scan - DeepSeek.html",
        r"C:\Users\HP\Downloads\Gemini Cloud Assist chat - Gemini for Cloud Co. - My First Project - Google Cloud console.html"
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
                if "disgrace" in line.lower():
                    print(f"File: {os.path.basename(fpath)} | Line {idx+1}: {line.strip()[:180]}")
        except Exception as e:
            print(f"Error reading {fpath}: {e}")

if __name__ == "__main__":
    main()
