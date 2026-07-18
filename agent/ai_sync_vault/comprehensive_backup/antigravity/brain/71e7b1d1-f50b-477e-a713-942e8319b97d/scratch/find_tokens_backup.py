import os

backup_dir = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\extracted_backup"

print("Searching backup for token or credential files...")
for root, dirs, files in os.walk(backup_dir):
    for file in files:
        if file in ["token.json", "credentials.json", "service_account.json"]:
            print(f"FOUND IN BACKUP: {os.path.join(root, file)}")
