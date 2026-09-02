# AI Directions — VSDE Steroids + Local→Host + Azure DevOps MCP (for other AI)

> Copy this file to your AI context. Follow exactly, non-destructive only (AGENTS.md Rule 2: never overwrite, create _v2/_v3 parallel).

## 0. Pre-checks (read-only)
- `git -C C:\OsintNeoAi status --porcelain` — must be on `main`, remote `https://github.com/Tonypost949/OsintNeoAi.git`
- `Test-Path C:\OsintNeoAi\OSINTNeoAiCLI.py` `C:\OsintNeoAi\public\syncfusion_grid.html` `C:\OsintNeoAi\data\tasks.json` `C:\OsintNeoAi\data\syncfusion_license.key`
- `az account show` — expect `anthony.dimarcello@students.post.edu` `f055033f-83fb-4ae9-9c36-be48f0c86158` `Azure for Students`, `az webapp list` → `osintneoai-app-949` `neoai-rg` `Running`
- `python -c "import flask"` `curl.exe --version` `rclone version`

## 1. Backup BEFORE every change (AGENTS.md:6 3 locations)
- GitHub: `git -C C:\OsintNeoAi push origin main`
- Local: `C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo\` — if `Users:RX` denied, fallback `C:\Users\AMD949~1\AppData\Local\Temp\opencode\`
- gdrive: `rclone lsd gdrive:` — if `401`, run `rclone config` → `gdrive` → refresh token → `rclone copy data/VSDE_STEROIDS_GUIDE_v2.md gdrive:Sharedall/OsintNeoAi/`

## 2. VSDE Steroids (my.visualstudio.com/benefits, Entra anthony.dimarcello@students.post.edu)
- License: Order `W753756` `Ngo9BigBOggjGyl/VkJ+Xk9GfVZLVGpUf1FrRmJJfV16cVxMZVVaRnZdRF1rS3hTdURhXXtfd3ZUTWNY`
- Backed: `data/syncfusion_license.key:1` + `data/syncfusion_license.key_amd949609:1`
- Tasks: `data/tasks.json:38` 8 tasks `TASK-VSDE-001..008` — 001 $9,995 DONE, 002 $100/mo DONE, 003 JetBrains, 004 Pluralsight, 005 Parasoft, 006 Atlas, 007 SSO DONE, 008 Deploy DONE
- Guide: `data/VSDE_STEROIDS_GUIDE_v2.md:1` + `data/VSDE_STEROIDS_CHECKLIST_v1.md:1`
- Portal: https://my.visualstudio.com/benefits → search JetBrains/Pluralsight/Parasoft → Get Code → redeem at jetbrains.com/pluralsight.com → set `data/tasks.json` status `IN_PROGRESS`→`DONE`
- Grid: `public/syncfusion_grid.html:7` `ej2/26.2.4` + `public/syncfusion_grid.html_v2:403` `ej.base.registerLicense(...)` + `vsdeData:408` toggle `public/syncfusion_grid_v3_steroids.html:1` duplicate

## 3. Make local work (OSINTNeoAiCLI.py:1428 port 5052)
```
python C:\OsintNeoAi\OSINTNeoAiCLI.py
# verify 200:
curl.exe -s -I http://127.0.0.1:5052/ ; curl.exe -s -I http://127.0.0.1:5052/syncfusion ; curl.exe -s -I http://127.0.0.1:5052/tasks ; curl.exe -s http://127.0.0.1:5052/api/tasks | head
```
- Must return 200 for `/`, `/syncfusion` (33002), `/tasks` (23636), `/api/tasks` (52 tasks)
- Original `OSINTNeoAiCLI.py` preserved, `OSINTNeoAiCLI_v2.py:1159` adds `/syncfusion` `/tasks` `/api/tasks` in parallel only

## 4. Host it (Azure App Service osintneoai-app-949 neoai-rg, startup.sh:4 `gunicorn --bind=0.0.0.0:8000 app:app`, app.py:1 `from OSINTNeoAiCLI import app`)
- Do NOT `az webapp deployment source sync` alone — large repo `.git 694MB` + `archive 2884MB` hangs Oryx `Running oryx build...` 08:52 stuck → 503
- Use minimal zip (whitelist, not blacklist):
```
python # create C:\Users\Amd949609\AppData\Local\Temp\opencode\host_minimal.zip with only app.py startup.sh requirements.txt OSINTNeoAiCLI.py .vscode/mcp.json public/* data/*
az webapp deploy --resource-group neoai-rg --name osintneoai-app-949 --src-path C:\Users\Amd949609\AppData\Local\Temp\opencode\host_minimal.zip --type zip
# expect 32s RuntimeSuccessful
curl.exe -s -I https://osintneoai-app-949.azurewebsites.net/syncfusion # expect 200 36153
curl.exe -s https://osintneoai-app-949.azurewebsites.net/api/tasks | head # expect TASK-VSDE-003:DONE after update
```
- If ExternalGit `https://github.com/Tonypost949/OsintNeoAi.git` `main` `ExternalGit` is needed, re-config then `git push` new commit + `az webapp deployment source sync`

## 5. Azure DevOps MCP (from https://prnt.sc/fA3cCceocWXm)
- Org `anthonydimarcello` `https://dev.azure.com/anthonydimarcello` Project `osintneoai`
- MCP URL `https://mcp.dev.azure.com/anthonydimarcello` `data/azure_devops_mcp_config.json:4`
- VS Code: `.vscode/mcp.json:3`:
```json
{"servers":{"azure-devops":{"type":"http","url":"https://mcp.dev.azure.com/anthonydimarcello"}}}
```
- Copilot → Settings → MCP Servers → Add `azure-devops` HTTP `https://mcp.dev.azure.com/anthonydimarcello` Save

## 6. Verify 3-location again
- `git log --oneline -3` → `8fd32d3` `a9e8549` etc.
- `curl.exe -s -I https://osintneoai-app-949.azurewebsites.net/` 200
- `rclone copy` fallback zip to temp if OneDrive `Users:RX` denied

## 7. Non-destructive rule checks
- Never delete: create `*_v2`, `*_v3_steroids.html`, `*.backup_20260827`
- Edit `data/tasks.json` only via `Add-Content` + `git add` small diff, keep `data/tasks.json.backup_20260827`
- Test locally `:5052` before `az webapp deploy`

## Quick one-liner to hand other AI:
```
Read data/AI_DIRECTIONS_STEROIDS_HOST_MCP.md, verify local python OSINTNeoAiCLI.py :5052 200, build whitelist host_minimal.zip (app.py startup.sh OSINTNeoAiCLI.py public data .vscode/mcp.json), az webapp deploy neoai-rg osintneoai-app-949, verify https://osintneoai-app-949.azurewebsites.net/syncfusion 200, update data/tasks.json TASK-VSDE-003 DONE via https://mcp.dev.azure.com/anthonydimarcello
```
