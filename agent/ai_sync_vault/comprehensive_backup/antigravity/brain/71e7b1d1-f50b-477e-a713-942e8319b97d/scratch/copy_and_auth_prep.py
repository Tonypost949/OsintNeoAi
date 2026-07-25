import shutil
import os

source_file = r"C:\Users\HP\Downloads\client_secret_226448795544-t3jkb6l3nu5ql06l8ebcdb5gks3ojeit.apps.googleusercontent.com.json"
dest_dir = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\.agents\skills\deep-osint\scripts"
dest_file = os.path.join(dest_dir, "credentials.json")

print(f"Copying and renaming credentials file...")
print(f"Source: {source_file}")
print(f"Destination: {dest_file}")

if os.path.exists(source_file):
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(source_file, dest_file)
    # Also copy to the workspace skill root just in case
    shutil.copy(source_file, os.path.join(r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\.agents\skills\deep-osint", "credentials.json"))
    print("SUCCESS: Credentials file copied and renamed successfully!")
else:
    print("ERROR: Source client secret file not found in Downloads.")
