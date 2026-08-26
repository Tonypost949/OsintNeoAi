import os
import urllib.request
import urllib.parse
import time

FILES = [
    ("1nGbKsudBlj5rhRjPwLKHJOeZZnDnGIDP", "3k units.png"),
    ("1G1CCZPCuhaZUCre8xq4NfU9BPsdcrIIj", "5star login pass maybe 2.png"),
    ("11hhjqXaK22Jic0FSVCaB4vyODx2YtreZ", "5star login pass maybe.png"),
    ("1_uuMKAOl9apOz7UodMLfnPIm-5SjA4hO", "9b4dd7da-fbac-499b-a44e-520945c7e823.pdf"),
    ("1BVvycAy4yingMqvG0aG34Kx9lGVPtk0R", "26-04132021_9855980 homeless deaths pat davis.pdf"),
    ("1yDsL_mNVfGkrfmFlWZEbugmNPs_RDtWF", "990MH2002.pdf"),
    ("1W-GANG1ilz8GyrIxnKKG-qNxnKk29lNd", "1963-04-15 engineer yamada.pdf"),
    ("1kSmb6zcNpt9m6C94btba5OuiV2hwCqWX", "1964-06-01 yamada.pdf"),
    ("16p5rh-7S9JypxEOEkyL9Jy9lrus9oRvZ", "1974-12-16 ten year service pin award yamada.pdf"),
    ("1fv9T-1-D1xrI02DUcwM70btv2pGQ_t21", "1978-09-13.pdf"),
    ("1lEQLViDCGuC2RTP227dhoO9ReIHSKAhS", "2015-08-04 - Easement Yamada Family Trust.pdf"),
    ("1LgEuSck8DuWpWU4WaSXEFwB9JxKy2eSj", "2017-112 homeleess report to california.pdf"),
    ("1za41a2eSpvYH9NKJm6k-JEV033qY5u-G", "2017-112 homeless report.pdf"),
    ("1mKulIUZyuqBXc14uxc3aSchoFTiHw7bd", "2018 state audit response homeless oc la.pdf"),
    ("1yv4Y773H3pFVVGB9GHZcHk0uNT3or265", "2021 dec phase 1 epa.pdf"),
    ("1UNtc8aqUXDSH4z8d1X8jzK3teC6cPWft", "7642 Wintersburg, California • Beyond Nevada Expeditions.html"),
    ("12wOrwLShs8gsEK6vyHf5jKUC6z6Cdiqu", "7942 speer apn new Withdrawn City Council Member Hardy Item for the April 6, 20.pdf"),
    ("13HT01PCfNcgjf5VfbpqVYSFiWFYXXYK-", "7942 speer plans Use Permit UPX1978058 - Plans.pdf"),
    ("1rRAVC5Jy8hXD306NKHXvNKYH099PZz-A", "17612 beach permits.Zip"),
    ("1I-AEKy5GU2JXb2XHwD4QN7xsdODYqVaI", "17642 beach 1962.png")
]

def main():
    target_dir = r"C:\OsintNeoAi\evidence\lawsuit_info_full_dimarcello"
    os.makedirs(target_dir, exist_ok=True)
    print(f"Archiving {len(FILES)} evidence files to {target_dir}...")
    
    success = 0
    for file_id, filename in FILES:
        dest = os.path.join(target_dir, filename)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            print(f"[ALREADY EXISTS] {filename} ({os.path.getsize(dest):,} bytes)")
            success += 1
            continue
            
        url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0"
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=30) as resp, open(dest, 'wb') as out_f:
                out_f.write(resp.read())
            sz = os.path.getsize(dest)
            print(f"[SAVED] {filename} ({sz:,} bytes)")
            success += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"[ERROR] {filename} (ID: {file_id}): {e}")

    print(f"\nDownload summary: {success}/{len(FILES)} files archived into evidence.")

if __name__ == "__main__":
    main()
