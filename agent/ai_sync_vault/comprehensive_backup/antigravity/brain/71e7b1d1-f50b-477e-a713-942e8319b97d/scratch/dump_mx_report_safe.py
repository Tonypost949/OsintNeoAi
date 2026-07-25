import os

path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\tablet_downloads\mx-report_hbpd.org_2026-06-29.txt"

if os.path.exists(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Safe printing using backslashreplace
    safe_content = content.encode('ascii', 'backslashreplace').decode('ascii')
    print("--- SAFE CONTENT ---")
    print(safe_content)
else:
    print("File does not exist!")
