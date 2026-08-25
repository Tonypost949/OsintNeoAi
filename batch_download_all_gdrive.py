import urllib.request
import os
import re
import json
import time

dest_dir = r'C:\Users\Amd949609\OsintNeoAi-1\evidence\google_drive'
os.makedirs(dest_dir, exist_ok=True)

# Full list of unique Google Drive URLs extracted from the entire repository
urls = [
    "https://docs.google.com/document/d/1Jt9FIzGKOhx2A0J779dcSjKYr6Gvw5dKRbUP8qRsvmw/edit",
    "https://docs.google.com/document/d/1RyMoIXbOIGIQn1BH-9fvuW1DgAHavXaYjwJiaLaFn48/edit",
    "https://docs.google.com/document/d/1WFjaBdavsupDhzXT8FhppvETCnQ-wIPTZTkg0gASj1I/edit",
    "https://docs.google.com/document/d/1YapNRDH0_cPwDDDedt-Q2hiPRvFqkZk-l1GtXzjrVX4/edit",
    "https://docs.google.com/document/d/1ZaPAI_hoR3KdMNEC0fqqylgMME_Ein-WNTA4VW4icRY/edit",
    "https://docs.google.com/document/d/1sJBBJnzMq14FD-K-MzoUL6cDaBaYgJdR_0Wzf5iBdTE/edit",
    "https://docs.google.com/document/d/1vMstdaAXVEfGmcYsyd_VcvolJMMOzg-cOGQhbKDQ6jU/edit",
    "https://docs.google.com/document/d/1ztXOo6RLqmpMPOhIXJZantMkn0voIh3TGwvYK14WSZ0/edit",
    "https://docs.google.com/document/u/0/d/1OjKkzaFo2vnuQRX-Al9PTH9G2itc7blMao9wvva4WSA/mobilebasic",
    "https://docs.google.com/document/u/0/d/1YjJP39icbyv9VX0z3QPUO8EiNTTSHHnhrvgytkRr7xE/mobilebasic",
    "https://docs.google.com/document/u/0/d/1qxaGS84s4BngrdM2O9nEuFq8lpr9HR1PoAMem5noNws/mobilebasic",
    "https://docs.google.com/document/u/4/d/1Jg5kWM-tODioiGrbIgjIkKy9eHNXpGQGuMvQ-bEeU-U/mobilebasic",
    "https://docs.google.com/document/u/4/d/1aiK_5Mf7a62r9E9iDX28BR-6KDw08q6Fa2UHigx2LbI/mobilebasic",
    "https://docs.google.com/document/u/4/d/1dqmhxxGqm4VwLcY2mZ0WNF4hE6qKKcf7uy3M4pYi2DU/mobilebasic",
    "https://docs.google.com/spreadsheets/d/10xr4HD2kAlpIukIcIEMAFzIa8zClAD7diZDymFoe-E8/edit",
    "https://docs.google.com/spreadsheets/d/12n33bjNmJZQNejz1fPFkHBQaqNSxthIFFvzLhLNURoQ/edit",
    "https://docs.google.com/spreadsheets/d/171xAuNcgcYP6-i4QJWKkZJE41l_jTa97mXpx5mnSWkU/edit",
    "https://docs.google.com/spreadsheets/d/18rtqh8EG2q1xBo2cLNyhIDuK9jrPGwYr9DI2UncoqJQ/edit",
    "https://docs.google.com/spreadsheets/d/1CJ6e9D_796VVs7cGbRfJqmL6I5cTSchPcqVOYbEz3Gc/edit",
    "https://docs.google.com/spreadsheets/d/1JxBbMt4JvGr--G0Pkl3jP9VDTBunR2uD3_faZXDvhxc/edit",
    "https://docs.google.com/spreadsheets/d/1O_19UfutQMD2rq18rFPnw7hsUf2tIvXn39hcQvWL5dY/edit",
    "https://docs.google.com/spreadsheets/d/1S0TVGS_Q299X6mft-HW2mvmWXuLRSp7SkFHHCER535k/edit",
    "https://docs.google.com/spreadsheets/d/1YCiJY00u8d3RqdQFXAeRWrvyi0uOgjKZdE33VDVv7EE/edit",
    "https://docs.google.com/spreadsheets/d/1Z5Dugxg6J5RgQjQ4oR-t_3yoAwfJhKlj3PhkdZroy2Y/edit",
    "https://docs.google.com/spreadsheets/d/1hKx1-8YnvrvAv9H6AQunli3dFSwsyIB3rF1yluO2Y1U/edit",
    "https://docs.google.com/spreadsheets/d/1n0Ei1CjrROzQyE-PaGvsBRoQY6Hf8L5o9VJ5gRG6Jno/edit",
    "https://docs.google.com/spreadsheets/d/1wpalg8Oc0g1i6zEGYjLqiWFmO-oibG4zalPQWCHBS88/edit",
    "https://drive.google.com/file/d/19YSnbXzlAxRkvRS6Qti-EgJRcJEGdIIo/view",
    "https://drive.google.com/file/d/1AcgqV5AOt2nl6njJLFn3HAcE-Z_5kPb7/view",
    "https://drive.google.com/file/d/1ITNzMbQkyAtftlRV50CHQ5zr0qmmzfI-/view",
    "https://drive.google.com/file/d/1TWPHhJSQoKvseLmJm5RkprQkF0iBQBAm/view",
    "https://drive.google.com/file/d/1W1dXpsnGdO_slXj_JipvosEqYUgT0U1q/view",
    "https://drive.google.com/file/d/1X11aun23RkIOrMSfXQhlPUUjGx0Do4X-/view",
    "https://drive.google.com/file/d/1ZHi6lkNAVHUQ3jf9axsgL_FPWR_eeXwe/view",
    "https://drive.google.com/file/d/1ZrHNJ1x-ZyA6cbWKBNCQMY35dBlXLI0J/view",
    "https://drive.google.com/file/d/1_K9DEng5uQKkrsCMh1_q4E1wJ85tFEXj/view",
    "https://drive.google.com/file/d/1hg5XKsgJPNscCLzis4mXs8ybP27eu-Ds/view",
    "https://drive.google.com/file/d/1i0MDI9bHPIV2WSwFLtnRsuYXMzJUognX/view",
    "https://drive.google.com/file/d/1joj7klSzVrgq3vcBNmgoDM2JJMioZzdp/view",
    "https://drive.google.com/file/d/1yYfXiAeQPX8DnD7aS_RMtAA9CKbi7_1F/view",
    "https://drive.google.com/open?id=1NdJVb9JNp28El2xf4tFNW4H1HR4CPkY7lNU4K8uzCDI",
    "https://drive.google.com/open?id=1OVy1fGBRna9bw_UUk7LJO8iQd8g3b_1t_2SbCmIfX3k",
    "https://drive.google.com/open?id=1Z7UGaokguutmGHwCsTrblbt00lXHGgjOl2r5f3bdz1E",
    "https://drive.google.com/open?id=1ax3swwQpiAK-LFbYZbVMR4DzXA_BpydEuw5q2i-pwPo"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

downloaded_items = []

for u in urls:
    doc_match = re.search(r'/document/(?:u/\d+/)?d/([a-zA-Z0-9_-]+)', u)
    sheet_match = re.search(r'/spreadsheets/(?:u/\d+/)?d/([a-zA-Z0-9_-]+)', u)
    file_match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', u)
    open_match = re.search(r'id=([a-zA-Z0-9_-]+)', u)
    
    file_id = None
    kind = 'file'
    
    if doc_match:
        file_id = doc_match.group(1)
        kind = 'doc'
    elif sheet_match:
        file_id = sheet_match.group(1)
        kind = 'sheet'
    elif file_match:
        file_id = file_match.group(1)
        kind = 'file'
    elif open_match:
        file_id = open_match.group(1)
        kind = 'open'

    if not file_id:
        continue

    # Prepare download targets based on kind
    download_urls = []
    if kind == 'doc':
        download_urls.append((f'https://docs.google.com/document/d/{file_id}/export?format=txt', f'gdoc_{file_id}.txt'))
        download_urls.append((f'https://docs.google.com/document/d/{file_id}/export?format=docx', f'gdoc_{file_id}.docx'))
    elif kind == 'sheet':
        download_urls.append((f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv', f'gsheet_{file_id}.csv'))
    else:
        download_urls.append((f'https://drive.google.com/uc?export=download&id={file_id}', f'gfile_{file_id}.bin'))

    for dl_url, filename in download_urls:
        target_path = os.path.join(dest_dir, filename)
        if os.path.exists(target_path) and os.path.getsize(target_path) > 500:
            continue

        try:
            req = urllib.request.Request(dl_url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                content = resp.read()
                if len(content) > 50 and not (b'<!DOCTYPE html>' in content and b'Google Drive - Page not found' in content):
                    with open(target_path, 'wb') as fh:
                        fh.write(content)
                    size_kb = round(len(content) / 1024, 1)
                    downloaded_items.append({
                        'id': file_id,
                        'file': filename,
                        'size_kb': size_kb,
                        'original_url': u
                    })
                    print(f"[+] Downloaded: {filename} ({size_kb} KB)")
        except Exception as e:
            # print(f"[-] Could not download {filename}: {e}")
            pass
        time.sleep(0.2)

print(f"\n[+] Total new assets archived: {len(downloaded_items)}")
