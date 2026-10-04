import os
import sys
import json
import subprocess
import io
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

class RcloneFile(io.RawIOBase):
    def __init__(self, rclone_path):
        self.rclone_path = rclone_path
        self.offset = 0
        
        # Get size using rclone size
        cmd = ["rclone", "size", rclone_path, "--json"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(res.stdout)
        self.size = info["bytes"]

    def seekable(self):
        return True

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.offset = offset
        elif whence == io.SEEK_CUR:
            self.offset += offset
        elif whence == io.SEEK_END:
            self.offset = self.size + offset
        return self.offset

    def tell(self):
        return self.offset

    def readinto(self, b):
        length = len(b)
        if self.offset >= self.size:
            return 0
        
        count = min(length, self.size - self.offset)
        cmd = ["rclone", "cat", self.rclone_path, "--offset", str(self.offset), "--count", str(count)]
        res = subprocess.run(cmd, capture_output=True)
        data = res.stdout
        b[:len(data)] = data
        self.offset += len(data)
        return len(data)

def scan_all_remote_zips():
    remote_dir = "gdrive:Sharedall/takeouts all 22226"
    print(f"[SCAN] Listing ZIP files in {remote_dir}...")
    
    cmd = ["rclone", "lsf", remote_dir, "--include", "*.zip"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    zip_files = [f.strip() for f in res.stdout.splitlines() if f.strip().endswith(".zip")]
    print(f"[SCAN] Found {len(zip_files)} ZIP files to scan.")
    
    targets = {
        "Records.json": "Takeout/Location History/Records.json",
        "Bookmarks.html": "Takeout/Chrome/Bookmarks.html",
        "All mail": "Takeout/Mail/All mail Including Spam and Trash.mbox"
    }
    
    found_locations = {}
    
    for idx, zip_name in enumerate(zip_files):
        full_path = f"{remote_dir}/{zip_name}"
        print(f"[{idx+1}/{len(zip_files)}] Scanning headers of {zip_name}...")
        try:
            rfile = RcloneFile(full_path)
            with zipfile.ZipFile(rfile) as z:
                names = z.namelist()
                for key, target_path in list(targets.items()):
                    # Match sub-string or exact path
                    matches = [n for n in names if target_path.lower() in n.lower()]
                    if matches:
                        print(f"[✓] Found match for '{key}' inside {zip_name}: {matches}")
                        found_locations[key] = {
                            "zip": zip_name,
                            "path_in_zip": matches[0]
                        }
                        # Remove to stop searching for this target
                        del targets[key]
        except Exception as e:
            print(f"[!] Error scanning {zip_name}: {e}")
            
        if not targets:
            print("[SCAN] All targets found! Ending scan.")
            break
            
    print("\n=== SCAN SUMMARY ===")
    print(json.dumps(found_locations, indent=2))
    
    # Save results to a file for subsequent stages to load
    with open("C:\\OsintNeoAi\\takeout_scan_results.json", "w") as f:
        json.dump(found_locations, f, indent=2)

if __name__ == "__main__":
    scan_all_remote_zips()
