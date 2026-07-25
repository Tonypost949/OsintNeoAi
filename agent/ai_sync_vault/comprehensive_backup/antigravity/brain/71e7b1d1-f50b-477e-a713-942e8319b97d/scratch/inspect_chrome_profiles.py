import os
import json

user_data_path = os.path.expandvars(r'%LocalAppData%\Google\Chrome\User Data')
print(f"Scanning User Data: {user_data_path}")

profiles = []
if os.path.exists(user_data_path):
    for item in os.listdir(user_data_path):
        item_path = os.path.join(user_data_path, item)
        if os.path.isdir(item_path):
            pref_path = os.path.join(item_path, 'Preferences')
            if os.path.exists(pref_path):
                try:
                    with open(pref_path, 'r', encoding='utf-8', errors='ignore') as f:
                        data = json.load(f)
                        
                        # 1. Try google services username
                        google_username = data.get('profile', {}).get('google_services_username') or ""
                        
                        # 2. Try profile name
                        name = data.get('profile', {}).get('name') or ""
                        
                        # 3. Try other accounts
                        account_info = data.get('account_info', [])
                        emails = []
                        if isinstance(account_info, list):
                            for acc in account_info:
                                if isinstance(acc, dict):
                                    em = acc.get('email') or acc.get('userName')
                                    if em:
                                        emails.append(em)
                        
                        profiles.append({
                            'dir': item,
                            'google_username': google_username,
                            'profile_name': name,
                            'emails': emails
                        })
                except Exception as e:
                    print(f"Error parsing {item}: {e}")

print("\nDetailed Chrome Profiles:")
for p in profiles:
    print(f"Profile Directory: {p['dir']}")
    print(f"  - Google Services Email: {p['google_username']}")
    print(f"  - Profile Name: {p['profile_name']}")
    if p['emails']:
        print(f"  - Associated Accounts: {', '.join(p['emails'])}")
    print("-" * 40)
