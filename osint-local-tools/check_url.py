import requests, urllib3
urllib3.disable_warnings()

url = 'https://admin.powerplatform.microsoft.com/manage/environments/environment/584c706d-38a2-e52e-b6e3-24a809f10508/hub?geo=Na'
r = requests.get(url, timeout=10, verify=False, allow_redirects=False)
print(f'Status: {r.status_code}')
if r.status_code in [301,302,303,307]:
    print(f'Redirect to: {r.headers.get("Location")}')
