import os
import zipfile
import shutil
import subprocess
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
live_html = root / 'gods_eye_view_live.html'

shutil.copy(live_html, root / 'hbnc_rico_gis.html')
shutil.copy(live_html, root / 'gods_eye_view.html')
shutil.copy(live_html, root / 'index.html')

zip_path = root / 'scratch' / 'light_azure_site_deploy.zip'

files_added = set()

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in root.glob('*.*'):
        if f.is_file() and f.suffix in ['.html', '.js', '.css', '.json']:
            rel_p = f.name
            if rel_p not in files_added:
                zf.write(f, rel_p)
                files_added.add(rel_p)

print(f"=== CREATED LIGHTWEIGHT AZURE SITE ZIP: {zip_path} ({zip_path.stat().st_size} bytes, {len(files_added)} files) ===")

cmd = f'az webapp deploy --name osintneoai-webapp --resource-group osintneoai-rg --src-path "{zip_path}" --type zip --output json 2>&1'
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if res.returncode == 0:
    print("✓ SUCCESS! Lightweight Azure App Service deployment completed successfully.")
    print("✓ Live GIS URL: https://osintneoai-webapp.azurewebsites.net/gods_eye_view_live.html")
    print("✓ Live Root URL: https://osintneoai-webapp.azurewebsites.net/")
else:
    print(f"Deployment output: {res.stdout or res.stderr}")
