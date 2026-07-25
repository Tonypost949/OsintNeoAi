import os

html_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\Official_GeoTracker_T10000018579\index.html"

if os.path.exists(html_path):
    with open(html_path, "r") as f:
        content = f.read()
        
    # Replace the local reference for the large Site Assessment Report with its direct Google Drive link
    content = content.replace(
        'href="T10000018579.20200625.Site Assessment Report.pdf"',
        'href="https://drive.google.com/file/d/1nNM0inix4fnAop9hErqeLk9-TKZUvzuy/view?usp=drivesdk"'
    )
    
    with open(html_path, "w") as f:
        f.write(content)
    print("[SUCCESS] Patched index.html to link directly to Google Drive for unsynced files!")
else:
    print("[ERROR] index.html not found.")
