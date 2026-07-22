import subprocess, zipfile, json, os, glob

CHUNK_DIR = r'G:\OsintNeoAi\takeout_chunks'
EXTRACT_DIR = r'G:\OsintNeoAi\takeout_metadata_extracted'

os.makedirs(EXTRACT_DIR, exist_ok=True)

zip_files = glob.glob(os.path.join(CHUNK_DIR, '*.zip'))
print(f'[CHUNK PROCESSOR] Found {len(zip_files)} completed zip chunks in {CHUNK_DIR}')

for zpath in zip_files:
    print(f'[EXTRACT METADATA] Reading {zpath}...')
    try:
        with zipfile.ZipFile(zpath, 'r') as zf:
            for item in zf.namelist():
                if item.endswith('.json') or item.endswith('.csv') or item.endswith('.mbox'):
                    zf.extract(item, EXTRACT_DIR)
                    print(f'  -> Extracted: {item}')
    except Exception as e:
        print(f'Error reading {zpath}: {e}')

print('[CHUNK PROCESSOR] Extraction of metadata files completed.')
