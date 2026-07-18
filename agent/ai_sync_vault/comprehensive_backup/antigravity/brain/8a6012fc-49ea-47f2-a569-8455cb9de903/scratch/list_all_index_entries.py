import json
import os

INDEX_FILE = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\drive_upload_index.json"

def main():
    if not os.path.exists(INDEX_FILE):
        print(f"[ERROR] Index file not found at: {INDEX_FILE}")
        return
        
    with open(INDEX_FILE, "r") as f:
        data = json.load(f)
        
    print(f"Total entries in index: {len(data)}")
    for i, item in enumerate(data):
        print(f"{i+1:3d}. {item.get('file_name')} ({item.get('mime_type')})")

if __name__ == "__main__":
    main()
