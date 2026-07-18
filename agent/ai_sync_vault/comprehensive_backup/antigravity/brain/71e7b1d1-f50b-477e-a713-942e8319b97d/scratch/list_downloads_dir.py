import os

downloads_path = r"C:\Users\HP\Downloads"
print(f"Listing directories in {downloads_path}:")
for item in os.listdir(downloads_path):
    item_path = os.path.join(downloads_path, item)
    if os.path.isdir(item_path):
        print(f"[DIR]  {item}")
    else:
        print(f"[FILE] {item} ({os.path.getsize(item_path)} bytes)")
