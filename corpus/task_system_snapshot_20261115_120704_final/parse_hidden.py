import subprocess
import re
import json

output = subprocess.getoutput("netsh wlan show networks mode=bssid")

# Parse SSIDs and BSSIDs
lines = output.splitlines()
networks = []
current_ssid = None
current_bssids = []

for line in lines:
    line_s = line.strip()
    if line_s.startswith("SSID "):
        if current_ssid is not None:
            networks.append({"ssid": current_ssid, "bssids": current_bssids})
        parts = line_s.split(" : ", 1)
        current_ssid = parts[1] if len(parts) > 1 else ""
        current_bssids = []
    elif line_s.startswith("BSSID "):
        parts = line_s.split(" : ", 1)
        bssid = parts[1] if len(parts) > 1 else ""
        current_bssids.append({"bssid": bssid, "details": {}})
    elif ":" in line_s and current_bssids:
        parts = line_s.split(":", 1)
        key = parts[0].strip()
        val = parts[1].strip()
        current_bssids[-1]["details"][key] = val

if current_ssid is not None:
    networks.append({"ssid": current_ssid, "bssids": current_bssids})

hidden_networks = [n for n in networks if n["ssid"] == ""]
print(f"Total networks: {len(networks)}")
print(f"Hidden networks found: {len(hidden_networks)}")
print(json.dumps(hidden_networks, indent=2))
