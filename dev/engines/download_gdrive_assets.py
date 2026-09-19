import urllib.request
import os
import json

dest_dir = r'C:\Users\Amd949609\OsintNeoAi-1\evidence\google_drive'
os.makedirs(dest_dir, exist_ok=True)

gdrive_files = [
    {
        'id': '1AcgqV5AOt2nl6njJLFn3HAcE-Z_5kPb7',
        'name': 'BUCK_RANCH_CALLENS_RANCH_GIS_ANALYSIS.pdf',
        'desc': 'Buck Ranch aka Callens Ranch Historical GIS Boundary Report',
        'url': 'https://drive.google.com/uc?export=download&id=1AcgqV5AOt2nl6njJLFn3HAcE-Z_5kPb7'
    },
    {
        'id': '1i0MDI9bHPIV2WSwFLtnRsuYXMzJUognX',
        'name': 'INDIAN_BURIAL_SEARCH_REPORT_1.pdf',
        'desc': 'Primary archaeological and archival survey on burial ground presence',
        'url': 'https://drive.google.com/uc?export=download&id=1i0MDI9bHPIV2WSwFLtnRsuYXMzJUognX'
    },
    {
        'id': '1X11aun23RkIOrMSfXQhlPUUjGx0Do4X-',
        'name': 'SOIL_ANALYSIS_BURIAL_GROUND_VERIFICATION.pdf',
        'desc': 'Scientific soil analysis evaluating markers vs historical burial claims',
        'url': 'https://drive.google.com/uc?export=download&id=1X11aun23RkIOrMSfXQhlPUUjGx0Do4X-'
    },
    {
        'id': '1W1dXpsnGdO_slXj_JipvosEqYUgT0U1q',
        'name': 'SOCAL_TRIBAL_TRUSTEES_MATRIX.csv',
        'desc': 'Cross-referenced matrix of Southern California tribal trustees and contacts',
        'url': 'https://drive.google.com/uc?export=download&id=1W1dXpsnGdO_slXj_JipvosEqYUgT0U1q'
    },
    {
        'id': '1ZHi6lkNAVHUQ3jf9axsgL_FPWR_eeXwe',
        'name': 'query_tribal_unclaimed.py',
        'desc': 'Python extraction engine for tribal unclaimed property',
        'url': 'https://drive.google.com/uc?export=download&id=1ZHi6lkNAVHUQ3jf9axsgL_FPWR_eeXwe'
    },
    {
        'id': '1ZrHNJ1x-ZyA6cbWKBNCQMY35dBlXLI0J',
        'name': 'trace_tribal_trustees.py',
        'desc': 'Python tracing engine for tribal trustees',
        'url': 'https://drive.google.com/uc?export=download&id=1ZrHNJ1x-ZyA6cbWKBNCQMY35dBlXLI0J'
    },
    {
        'id': '1ZfxgYiowD_svrrLCxgIMPDv-aHTNfjSDxIC6PclDVFE',
        'name': 'DR_ANN_VERMA_RESCISSION_NOTICE.docx',
        'desc': 'Formal Rescission Notice & Protected Whistleblower Statement of Dr. Ann Verma',
        'url': 'https://docs.google.com/document/d/1ZfxgYiowD_svrrLCxgIMPDv-aHTNfjSDxIC6PclDVFE/export?format=docx'
    },
    {
        'id': '1ZfxgYiowD_svrrLCxgIMPDv-aHTNfjSDxIC6PclDVFE',
        'name': 'DR_ANN_VERMA_RESCISSION_NOTICE.txt',
        'desc': 'Text export of Rescission Notice of Dr. Ann Verma',
        'url': 'https://docs.google.com/document/d/1ZfxgYiowD_svrrLCxgIMPDv-aHTNfjSDxIC6PclDVFE/export?format=txt'
    }
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

downloaded_files = []

for item in gdrive_files:
    target_path = os.path.join(dest_dir, item['name'])
    print(f"[*] Downloading {item['name']} from Google Drive...")
    try:
        req = urllib.request.Request(item['url'], headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read()
            # If Google Drive returned an HTML confirmation page instead of raw file
            if b'<!DOCTYPE html>' in content and (b'Google Drive - Virus scan warning' in content or b'download_warning' in content):
                print(f"  [!] Warning page returned for {item['name']}, handling confirmation token...")
                import re
                confirm_match = re.search(r'confirm=([0-9A-Za-z_]+)', content.decode('utf-8', errors='ignore'))
                if confirm_match:
                    confirm_token = confirm_match.group(1)
                    confirm_url = f"{item['url']}&confirm={confirm_token}"
                    req2 = urllib.request.Request(confirm_url, headers=headers)
                    with urllib.request.urlopen(req2, timeout=20) as resp2:
                        content = resp2.read()
            
            with open(target_path, 'wb') as fh:
                fh.write(content)
            size_kb = round(len(content) / 1024, 1)
            print(f"  [+] Saved {item['name']} ({size_kb} KB)")
            downloaded_files.append({
                'name': item['name'],
                'path': target_path,
                'size_kb': size_kb,
                'desc': item['desc'],
                'gdrive_id': item['id']
            })
    except Exception as e:
        print(f"  [-] Failed to download {item['name']}: {e}")

manifest_path = os.path.join(dest_dir, 'GDRIVE_INGESTION_MANIFEST.json')
with open(manifest_path, 'w', encoding='utf-8') as mf:
    json.dump(downloaded_files, mf, indent=2)

print(f"\n[+] Total Google Drive files successfully moved into repo: {len(downloaded_files)}")
