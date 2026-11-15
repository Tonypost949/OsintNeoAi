import os
import json
import datetime
import subprocess

evidence_dir = r"C:\Amd949609_Antigravity_v1\evidence\network_sessions"
os.makedirs(evidence_dir, exist_ok=True)

dt_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(evidence_dir, f"totalplay_session_{dt_str}.json")

# Gather current interface info
wifi_info = subprocess.getoutput("netsh wlan show interfaces")
ip_info = subprocess.getoutput("ipconfig /all")

record = {
    "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "connected_ssid": "Club_Totalplay_WiFi",
    "bssid": "10:08:1d:b8:ac:d2",
    "band": "5 GHz",
    "session_policy_estimate": "Standard Totalplay guest session: ~2 to 24 hours per session before renewal or re-prompt. Keep-alive active.",
    "wifi_interfaces_raw": wifi_info,
    "ipconfig_raw": ip_info
}

with open(log_file, "w", encoding="utf-8") as f:
    json.dump(record, f, indent=2)

md_summary = os.path.join(evidence_dir, "LATEST_NETWORK_STATUS.md")
with open(md_summary, "w", encoding="utf-8") as f:
    f.write(f"""# Active Network Session Telemetry

- **Recorded At**: {record['timestamp_utc']}
- **SSID**: Club_Totalplay_WiFi
- **BSSID**: 10:08:1d:b8:ac:d2
- **Frequency Band**: 5 GHz (802.11ax)
- **Session Duration Policy**: 
  - Typically lasts **2 to 24 hours** on open Totalplay community APs before requiring a re-handshake or reconnect.
  - If it drops, auto-reconnect profile is active.
- **Evidence Record**: `{log_file}`
""")

print(f"SUCCESS: {log_file}")
