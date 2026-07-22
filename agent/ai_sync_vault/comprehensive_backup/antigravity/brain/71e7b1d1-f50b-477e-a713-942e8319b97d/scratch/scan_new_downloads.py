import os

downloads_dir = r"C:\Users\HP\Downloads"

print(f"Scanning downloads folder for new files: {downloads_dir}")
if os.path.exists(downloads_dir):
    files_with_time = []
    for root, dirs, filenames in os.walk(downloads_dir):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            try:
                mtime = os.path.getmtime(filepath)
                files_with_time.append((filepath, mtime))
            except Exception:
                pass
    
    # Sort by modification time descending (newest first)
    files_with_time.sort(key=lambda x: x[1], reverse=True)
    
    print("\nMost recent files in Downloads:")
    for filepath, mtime in files_with_time[:15]:
        import datetime
        time_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        size_kb = os.path.getsize(filepath) / 1024
        print(f"[{time_str}] {os.path.basename(filepath)} ({size_kb:.1f} KB) -> {filepath}")
else:
    print("Downloads directory not found.")
