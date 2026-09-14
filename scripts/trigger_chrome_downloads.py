import subprocess
import time

job_id = "d931df5f-2c2e-458a-9078-6f722c982eb9"
user_id = "107365263735013302947"

# Full range of all 37 export chunks from her September 2026 Takeout:
# Part 0 (MBOX), Parts 1-31 (Photos), Parts 32-37 (Drive, Chrome, Activity, Settings)
all_indices = list(range(0, 38))

print(f"[TRIGGER] Launching download requests for ALL {len(all_indices)} Takeout parts (Indices 0-37)...")

for i in all_indices:
    url = f"https://takeout.google.com/takeout/download?j={job_id}&i={i}&user={user_id}"
    print(f"  -> Triggering download URL for part {i}...")
    subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process chrome.exe '{url}'"])
    time.sleep(1.5)

print("[✓] All 37 Takeout part download requests launched in Chrome!")
