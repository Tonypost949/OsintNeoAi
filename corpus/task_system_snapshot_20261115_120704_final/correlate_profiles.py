import subprocess
import time
import json
import os

evidence_dir = r"C:\Amd949609_Antigravity_v1\evidence\network_sessions"
os.makedirs(evidence_dir, exist_ok=True)

# List all saved Wi-Fi profiles
profiles_raw = subprocess.getoutput("netsh wlan show profiles")
profile_names = []
for line in profiles_raw.splitlines():
    if "All User Profile" in line:
        parts = line.split(":", 1)
        if len(parts) > 1:
            profile_names.append(parts[1].strip())

print(f"Total saved profiles on machine: {len(profile_names)}")

# Look specifically for INFINITUM, Totalplay, Amped, or Tony profiles
priority_candidates = [
    p for p in profile_names 
    if any(k in p.lower() for k in ["infinitum", "totalplay", "tony", "amped", "cfe", "repeater"])
]

print("Priority saved profiles to analyze:")
for p in priority_candidates:
    print(f" - {p}")

# Write analysis to file
report_path = os.path.join(evidence_dir, "HIDDEN_NETWORK_INVESTIGATION.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump({
        "strongest_hidden_bssid": "ca:3a:6b:1e:ce:7c",
        "signal": "85%",
        "band": "5 GHz, Channel 149",
        "device_arp_history": "10.203.24.213 (MAC: c8:3a:6b:1e:ce:7c - identical OUI prefix)",
        "priority_saved_profiles": priority_candidates
    }, f, indent=2)

print(f"Saved investigation report to: {report_path}")
