import os

docs_path = r"C:\Users\HP\OneDrive\Documents"
print(f"Listing files in {docs_path}:")
for item in os.listdir(docs_path):
    item_path = os.path.join(docs_path, item)
    if os.path.isdir(item_path):
        print(f"[DIR]  {item}")
    else:
        print(f"[FILE] {item} ({os.path.getsize(item_path)} bytes)")
