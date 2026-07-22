import os
import json
import subprocess
import sys

user_data_path = os.path.expandvars(r'%LocalAppData%\Google\Chrome\User Data')
preferences_files = []

# Walk to find Preferences files
if os.path.exists(user_data_path):
    for root, dirs, files in os.walk(user_data_path):
        if 'Preferences' in files:
            # We want only top-level profiles (e.g. Default, Profile 1, Profile 2)
            rel_path = os.path.relpath(root, user_data_path)
            parts = rel_path.split(os.sep)
            if len(parts) == 1:
                preferences_files.append((parts[0], os.path.join(root, 'Preferences')))

target_profile = None
profiles_found = []

for profile_name, pref_path in preferences_files:
    try:
        with open(pref_path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            # Retrieve email or account info
            account_info = data.get('profile', {})
            email = account_info.get('google_services_username') or account_info.get('name') or ""
            profiles_found.append((profile_name, email))
            if 'amd949609' in email.lower():
                target_profile = profile_name
    except Exception as e:
        pass

print("Profiles found:")
for name, email in profiles_found:
    print(f" - {name}: {email}")

if not target_profile:
    # Fallback to Default or Profile 1 if amd949609 not found
    print("Could not find a profile explicitly matching 'amd949609'. Searching for 'txtdjdrop' or using Default.")
    for name, email in profiles_found:
        if 'txtdjdrop' in email.lower():
            target_profile = name
            break
    if not target_profile and profiles_found:
        target_profile = profiles_found[0][0]
    else:
        target_profile = 'Default'

print(f"Selected profile for launch: {target_profile}")

extension_path = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\qag2-osint-extension"
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

cmd = [
    chrome_path,
    f"--profile-directory={target_profile}",
    f"--load-extension={extension_path}",
    "chrome://extensions/"
]

print(f"Executing: {' '.join(cmd)}")
subprocess.Popen(cmd, shell=True)
print("Chrome launched successfully with the extension pre-loaded!")
