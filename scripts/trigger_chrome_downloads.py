import subprocess
import time

job_id = "d931df5f-2c2e-458a-9078-6f722c982eb9"
user_id = "107365263735013302947"

# Part indices: 0 through 37
# Indices 0-5 and 37 cover the Location, Mbox, Drive, Chrome, and Core Intelligence
indices = [0, 1, 2, 3, 4, 5, 37]

for i in indices:
    url = f"https://takeout.google.com/takeout/download?j={job_id}&i={i}&user={user_id}"
    print(f"[TRIGGER] Launching download for part {i}...")
    subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process chrome.exe '{url}'"])
    time.sleep(2)

print("[✓] All download requests launched in Chrome!")
