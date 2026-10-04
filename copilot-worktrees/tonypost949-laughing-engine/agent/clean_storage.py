import os
from google.cloud import storage

BUCKET_NAME = "osint-ai-evidence-vault-m4"
GCS_FOLDER = "pc_backup/downloads_cleanup/"
DOWNLOADS_DIR = r"C:\Users\HP\Downloads"

def clean_large_files():
    print(f"--- CLEANING LARGE FILES IN {DOWNLOADS_DIR} ---")
    
    # Get all files in Downloads
    files = []
    for f in os.listdir(DOWNLOADS_DIR):
        path = os.path.join(DOWNLOADS_DIR, f)
        if os.path.isfile(path):
            files.append((path, os.path.getsize(path)))
            
    # Sort by size, descending
    files.sort(key=lambda x: x[1], reverse=True)
    
    # Pick the top 10 largest files (e.g. installers, old zip backups)
    top_10 = files[:10]
    
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        
        freed_bytes = 0
        for path, size in top_10:
            file_name = os.path.basename(path)
            blob_path = f"{GCS_FOLDER}{file_name}"
            print(f"Uploading {file_name} (Size: {size / (1024**2):.1f} MB)...")
            
            blob = bucket.blob(blob_path)
            # Use 5MB chunk size for upload reliability and set a longer timeout
            blob.chunk_size = 5 * 1024 * 1024
            blob.upload_from_filename(path, timeout=600)
            
            print(f"[OK] Uploaded to gs://{BUCKET_NAME}/{blob_path}")
            
            # Delete local file to free space
            os.remove(path)
            freed_bytes += size
            print(f"[DEL] Deleted local file: {path}")
            
        print("-" * 40)
        print(f"Successfully freed {freed_bytes / (1024**3):.2f} GB of space!")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    clean_large_files()
