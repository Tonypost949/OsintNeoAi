import json
import os

INDEX_FILE = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\drive_upload_index.json"

def main():
    if not os.path.exists(INDEX_FILE):
        print(f"[ERROR] Index file not found at: {INDEX_FILE}")
        return
        
    with open(INDEX_FILE, "r") as f:
        data = json.load(f)
        
    print(f"[*] Total indexed files: {len(data)}")
    
    # Filter for files with 2025 in their created/modified time or matching keywords
    keywords = ["edr", "esa", "environmental", "report", "cameron", "beach", "toxic", "chromium", "lead", "soil", "waterboard", "yamada", "knabb"]
    
    results = []
    for item in data:
        name = item.get("file_name", "").lower()
        created = item.get("created_time", "")
        modified = item.get("modified_time", "")
        
        # Check if 2025 is in the timestamps
        is_2025 = "2025" in created or "2025" in modified
        
        # Check if any keyword matches
        kw_match = any(kw in name for kw in keywords)
        
        if is_2025 or kw_match:
            results.append(item)
            
    print(f"[*] Found {len(results)} matching files:")
    for r in results:
        print(f"  - Name: {r['file_name']}")
        print(f"    Created: {r['created_time']} | Modified: {r['modified_time']}")
        print(f"    Size: {r['size_bytes']} bytes")
        print(f"    Link: {r.get('web_view_link')}")
        print("-" * 50)

if __name__ == "__main__":
    main()
