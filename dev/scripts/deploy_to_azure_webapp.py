import os
import zipfile
import subprocess
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
live_html = root / 'gods_eye_view_live.html'
zip_path = root / 'scratch' / 'azure_dashboard_deploy.zip'

zip_path.parent.mkdir(parents=True, exist_ok=True)

# Build zip archive
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(live_html, 'gods_eye_view_live.html')
    zf.write(live_html, 'gods_eye_view.html')
    zf.write(live_html, 'index.html')

print(f"=== CREATED DEPLOYMENT ZIP: {zip_path} ({zip_path.stat().st_size} bytes) ===")

targets = [
    {'name': 'osintneoai-app-949', 'rg': 'neoai-rg'},
    {'name': 'osintneoai-webapp', 'rg': 'osintneoai-rg'}
]

for t in targets:
    print(f"\n🚀 Deploying to Azure Web App: {t['name']} (Resource Group: {t['rg']})...")
    cmd = f"az webapp deployment source config-zip --name {t['name']} --resource-group {t['rg']} --src \"{zip_path}\" 2>&1"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✓ SUCCESS! Deployed to https://{t['name']}.azurewebsites.net/gods_eye_view_live.html")
        print(f"✓ LIVE URL: https://{t['name']}.azurewebsites.net/gods_eye_view.html")
        print(f"✓ LIVE URL: https://{t['name']}.azurewebsites.net/")
    else:
        print(f"❌ Deployment failed for {t['name']}: {res.stderr or res.stdout}")
