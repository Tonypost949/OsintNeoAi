import zipfile
import os

zip_path = r"C:\Users\HP\OneDrive\Documents\drive-download-20260629T205840Z-3-001.zip"
extract_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted"

os.makedirs(extract_dir, exist_ok=True)

print(f"Extracting text files from {zip_path} to {extract_dir}...")

text_extensions = {'.txt', '.md', '.log'}

extracted_count = 0
try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        for info in z.infolist():
            # Check if it's a file and has a text extension
            _, ext = os.path.splitext(info.filename)
            if ext.lower() in text_extensions:
                # Resolve destination path
                dest_path = os.path.join(extract_dir, info.filename)
                # Ensure directory exists
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                # Extract file
                with z.open(info) as source, open(dest_path, 'wb') as target:
                    target.write(source.read())
                extracted_count += 1
                if extracted_count % 20 == 0:
                    print(f"Extracted {extracted_count} files...")
                    
    print(f"\nSUCCESS! Extracted a total of {extracted_count} text/markdown/log files.")
except Exception as e:
    print(f"Error during extraction: {e}")
