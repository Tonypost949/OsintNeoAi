import os
import zipfile
import shutil
import subprocess
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
live_html = root / 'gods_eye_view_live.html'

# Synchronize HTML files locally
shutil.copy(live_html, root / 'hbnc_rico_gis.html')
shutil.copy(live_html, root / 'gods_eye_view.html')
shutil.copy(live_html, root / 'public' / 'hbnc_rico_gis.html')
shutil.copy(live_html, root / 'public' / 'gods_eye_view_live.html')
shutil.copy(live_html, root / 'public' / 'gods_eye_view.html')

zip_path = root / 'scratch' / 'clean_azure_site_deploy.zip'

files_added = set()

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    pub_dir = root / 'public'
    if pub_dir.exists():
        for pf in pub_dir.glob('**/*.*'):
            if pf.is_file():
                rel_p = str(pf.relative_to(pub_dir)).replace('\\', '/')
                if rel_p not in files_added:
                    zf.write(pf, rel_p)
                    files_added.add(rel_p)

print(f"=== CREATED CLEAN AZURE SITE ZIP: {zip_path} ({zip_path.stat().st_size} bytes, {len(files_added)} files) ===")

cmd = f'az webapp deploy --name osintneoai-webapp --resource-group osintneoai-rg --src-path "{zip_path}" --type zip --output json 2>&1'
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if res.returncode == 0:
    print("✓ SUCCESS! Clean Azure App Service deployment completed successfully.")
    print("✓ Live Site URL: https://osintneoai-webapp.azurewebsites.net/hbnc_rico_gis.html")
else:
    print(f"Deployment output: {res.stdout or res.stderr}")
