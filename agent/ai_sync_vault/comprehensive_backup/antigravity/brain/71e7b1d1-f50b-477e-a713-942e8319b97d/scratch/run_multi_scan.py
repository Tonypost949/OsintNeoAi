import subprocess
import os
from datetime import datetime

# Target directories on C:\ and the user folder
targets = [
    r"C:\OSINTNEOAIXL",
    r"C:\OSINT_HB_Data",
    r"C:\OSINT_Investigation_Anthony",
    r"C:\maltego_osint",
    r"C:\Users\HP"
]

outdir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
scanner_script = r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\.agents\skills\deep-osint\scripts\core_scanner.py"

print("Starting custom multi-target OSINT scans...")

for target in targets:
    if os.path.exists(target):
        print(f"\nScanning: {target}")
        try:
            # We run core_scanner.py for each specific folder to generate target-specific sheets
            cmd = ["python", scanner_script, "--root", target, "--outdir", outdir]
            subprocess.run(cmd, check=True)
            print(f"Completed scan of: {target}")
        except Exception as e:
            print(f"Error scanning {target}: {e}")
    else:
        print(f"Skipping (not found): {target}")

print("\nAll targeted scans completed successfully.")
