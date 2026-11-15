import subprocess

profiles = [
    "INFINITUM9417_5",
    "INFINITUM9417_2.4",
    "INFINITUM9417",
    "Totalplay-AFA5",
    "Repeater_FC8912",
    "Amped_Wireless"
]

for p in profiles:
    cmd = f'netsh wlan set profileparameter name="{p}" nonBroadcast=yes'
    res = subprocess.getoutput(cmd)
    print(f"{p}: {res.strip()}")
