import os
import shutil
import zipfile

ROOT_DIR = r"C:\OSINTNEOAI"
CLOUD_DIR = os.path.join(ROOT_DIR, "cloud_deploy")
ZIP_PATH = os.path.join(ROOT_DIR, "makavelli", "OSINTNEOAI_FINAL_CLOUD_PACK.zip")

os.makedirs(CLOUD_DIR, exist_ok=True)

# 1. Write Procfile
with open(os.path.join(CLOUD_DIR, "Procfile"), "w", encoding="utf-8") as f:
    f.write("web: gunicorn --bind=0.0.0.0 --timeout 600 app:app\n")

# 2. Copy app.py
shutil.copyfile(os.path.join(ROOT_DIR, "app.py"), os.path.join(CLOUD_DIR, "app.py"))

# 3. Copy requirements.txt
shutil.copyfile(os.path.join(ROOT_DIR, "requirements.txt"), os.path.join(CLOUD_DIR, "requirements.txt"))

# 4. Copy api directory
api_dest = os.path.join(CLOUD_DIR, "api")
if os.path.exists(api_dest):
    shutil.rmtree(api_dest)
shutil.copytree(os.path.join(ROOT_DIR, "api"), api_dest)

# 5. Copy Avatars and Banners
shutil.copyfile(
    os.path.join(ROOT_DIR, "makavelli", "avatar", "circular_transparent.png"),
    os.path.join(CLOUD_DIR, "OSINT_NEO_AI_circular_avatar_transparent.png")
)
shutil.copyfile(
    os.path.join(ROOT_DIR, "makavelli", "avatar", "banner_black.png"),
    os.path.join(CLOUD_DIR, "osint_neo_ai_banner.png")
)

# 6. Write DEPLOY_TO_CLOUD.ps1
deploy_ps1 = """# Auto-Deploy to Azure Cloud Webhook App
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 Deploying OSINTNeoAi 24/7 Cloud Engine" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
az.cmd webapp deploy --resource-group neoai-rg --name osintneoai-app-949 --src-path "$CurrentDir" --type zip

Write-Host "`n✅ Cloud Deployment Complete!" -ForegroundColor Green
Write-Host "Webhook URL: https://osintneoai-app-949.azurewebsites.net/webhook"
Write-Host "Verify Token: makaveli_osint_verify_2026"
pause
"""
with open(os.path.join(CLOUD_DIR, "DEPLOY_TO_CLOUD.ps1"), "w", encoding="utf-8") as f:
    f.write(deploy_ps1)

# 7. Write DEPLOY_README.txt
readme_text = """========================================================================
OSINTNEOAI FINAL CLOUD PACK — 24/7 AUTONOMOUS WEBHOOK ENGINE
========================================================================

CLOUD ENDPOINTS:
- Azure Webhook: https://osintneoai-app-949.azurewebsites.net/webhook
- Verify Token: makaveli_osint_verify_2026
- Facebook Page ID: 61594100636376
- Makaveli Web HUD: https://tonypost949.github.io/OsintNeoAi/makavelli/

HOW IT WORKS:
1. When anyone tags @OSINTNeoAi or @makaveli on Facebook, Meta sends a webhook to Azure.
2. Azure processes the comment via Makaveli OSINT Agent and replies instantly.
3. Zero PC dependency — runs 24/7/365 in Microsoft Cloud.
"""
with open(os.path.join(CLOUD_DIR, "DEPLOY_README.txt"), "w", encoding="utf-8") as f:
    f.write(readme_text)

# 8. Package to ZIP
with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(CLOUD_DIR):
        for file in files:
            full_p = os.path.join(root, file)
            rel_p = os.path.relpath(full_p, CLOUD_DIR)
            z.write(full_p, rel_p)

print(f"[SUCCESS] Built: {ZIP_PATH} and {CLOUD_DIR}")
