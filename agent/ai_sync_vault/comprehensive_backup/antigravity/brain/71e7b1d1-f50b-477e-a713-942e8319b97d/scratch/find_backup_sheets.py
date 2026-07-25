import os

backup_dir = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\extracted_backup"
print(f"Scanning {backup_dir} for csv/xlsx files...")

found = []
for root, dirs, files in os.walk(backup_dir):
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in ['.csv', '.xlsx']:
            fp = os.path.join(root, f)
            size = os.path.getsize(fp)
            found.append((fp, size))

print(f"\nFound {len(found)} spreadsheet/CSV files in backup:")
for fp, size in sorted(found, key=lambda x: x[1], reverse=True):
    print(f"- {fp} ({size} bytes)")
