import os
import json
import re

downloads_path = r"C:\Users\HP\Downloads"

def search_files():
    results = []
    # Let's search for common patterns of lists of names (e.g. capitalized First Last, or names followed by age/address, or tables)
    # Also look for files containing "Truthfinder" or "Report"
    for filename in os.listdir(downloads_path):
        if filename.endswith(('.txt', '.json', '.md', '.csv')):
            file_path = os.path.join(downloads_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Search for occurrences of Beach or Cameron in proximity to names
                    # Or look for tables of people
                    print(f"Scanning {filename} ({len(content)} bytes)...")
                    
                    # If it's JSON, let's parse it and search fields
                    if filename.endswith('.json'):
                        try:
                            data = json.loads(content)
                            # Custom search in json
                            str_data = json.dumps(data)
                            if "cameron" in str_data.lower() or "beach" in str_data.lower():
                                print(f"  -> Found Beach/Cameron in JSON file: {filename}")
                        except Exception as je:
                            pass
                            
                    # Let's look for specific patterns like "Truthfinder", "names", "homeless", "residents"
                    matches = re.findall(r'(?i)(?:truthfinder|resident|homeless|shelter|cameron|beach|name).*?[\n\r]+.*', content)
                    if matches:
                        print(f"  -> Found {len(matches)} potential context matches in {filename}")
                        
            except Exception as e:
                print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    search_files()
