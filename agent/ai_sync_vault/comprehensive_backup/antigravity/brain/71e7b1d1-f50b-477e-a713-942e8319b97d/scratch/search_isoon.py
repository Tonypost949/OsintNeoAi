import os

downloads_path = r"C:\Users\HP\Downloads"
search_terms = ["isoon", "i-soon", "anxun", "an-xun", "apt", "chinese", "leak"]

print("Scanning C:\\Users\\HP\\Downloads for I-Soon / Anxun / APT related files...")
found = []

for root, dirs, files in os.walk(downloads_path):
    for dir_name in dirs:
        dir_lower = dir_name.lower()
        for term in search_terms:
            if term in dir_lower:
                path = os.path.join(root, dir_name)
                found.append(("directory", path, term))
                print(f"FOUND DIRECTORY: {path} (matched '{term}')")
                break
                
    for file_name in files:
        file_lower = file_name.lower()
        for term in search_terms:
            if term in file_lower:
                path = os.path.join(root, file_name)
                found.append(("file", path, term))
                print(f"FOUND FILE: {path} (matched '{term}')")
                break

print(f"Scan complete. Total matches found: {len(found)}")
