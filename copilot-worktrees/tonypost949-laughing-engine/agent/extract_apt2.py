import requests
import json
import os
import zipfile

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")

with open(TOKEN_FILE, 'r') as f:
    creds = json.load(f)
    
token = creds['token']

file_id = "1PMaumLhejJmJkjv2r6PXhWhRYXmP5-Ss"
file_name = r"G:\osint-agent\APT2024filesfull.zip"
extract_dir = r"G:\osint-agent\APT2024_Extracted"

url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
headers = {"Authorization": f"Bearer {token}"}

print(f"Downloading to {file_name} via requests streaming...")

with requests.get(url, headers=headers, stream=True) as r:
    r.raise_for_status()
    total_size = int(r.headers.get('content-length', 0))
    downloaded = 0
    with open(file_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*1024*10): # 10MB chunks
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = int((downloaded / total_size) * 100)
                    print(f"Downloaded {percent}% ({downloaded / (1024*1024):.2f} MB)")
                else:
                    print(f"Downloaded {downloaded / (1024*1024):.2f} MB")

print("Download complete. Extracting...")
os.makedirs(extract_dir, exist_ok=True)
with zipfile.ZipFile(file_name, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

print(f"Extraction complete. Files are in: {extract_dir}")
for root, dirs, files in os.walk(extract_dir):
    for f in files:
        print(f" - {f}")
