import os

src = r"C:\Users\HP\OneDrive\Imports\txtdjdrop@gmail.com - Google Drive\bids hb\T10000018579.20200625.Site Assessment Report.pdf"
dest = r"C:\Users\HP\OneDrive\Documents\opencode_work\Official_GeoTracker_T10000018579\T10000018579.20200625.Site Assessment Report.pdf"

print(f"[*] Retrying copy of {os.path.basename(src)} using direct stream transfer...")
try:
    if not os.path.exists(src):
        print(f"[ERROR] Source file does not exist: {src}")
        exit(1)
        
    # Read/write chunk-by-chunk to force OneDrive to sync the block stream
    with open(src, "rb") as fsrc:
        with open(dest, "wb") as fdest:
            print("    Streaming bytes (this may take a few seconds as OneDrive pulls the file)...")
            chunk_count = 0
            while True:
                chunk = fsrc.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                fdest.write(chunk)
                chunk_count += 1
                if chunk_count % 10 == 0:
                    print(f"    Transferred: {chunk_count} MB")
                    
    print("[SUCCESS] Site Assessment Report successfully downloaded and staged!")
except Exception as e:
    print(f"[ERROR] Failed during direct stream copy: {e}")
