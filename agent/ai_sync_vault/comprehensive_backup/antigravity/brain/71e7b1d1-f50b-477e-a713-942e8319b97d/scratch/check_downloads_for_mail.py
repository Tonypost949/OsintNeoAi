import os

downloads_dir = r"C:\Users\HP\Downloads"

print(f"Scanning downloads folder: {downloads_dir}")
if os.path.exists(downloads_dir):
    for root, dirs, files in os.walk(downloads_dir):
        for file in files:
            if file in ['credentials.json', 'token.json'] or file.lower().endswith(('.eml', '.mbox', '.pst', '.msg', '.zip')):
                # Only list files directly in Downloads or recent subfolders to avoid listing too much
                filepath = os.path.join(root, file)
                print(f"FOUND: {filepath}")
else:
    print("Downloads folder not found.")
