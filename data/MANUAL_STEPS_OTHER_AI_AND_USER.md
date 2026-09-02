# MANUAL STEPS — Requires Your Browser (Other AI Cannot Do Alone)

> Autonomous work done: local :5052 200, hosted https://osintneoai-app-949.azurewebsites.net 200, GitHub 8fd32d3+fa05dc6, minimal zip 1.1MB deployed, MCP https://mcp.dev.azure.com/anthonydimarcello live. These steps need human Entra click.

## 1. VSDE Steroids — 3 Portal Clicks (5 min total, anthony.dimarcello@students.post.edu)

**Portal:** https://my.visualstudio.com/benefits  (already authed for W753756 $9,995)

- **TASK-VSDE-004 Pluralsight/DataCamp $1,200** (data/tasks.json:54 `IN_PROGRESS`→`DONE` locally but verify):
  Search `Pluralsight` → Activate 6mo → copy link → do same for `DataCamp` → paste codes here. I will write to `data/pluralsight_key_amd949609.txt` and redeploy.

- **TASK-VSDE-005 Parasoft/Termius $2,400**:
  Search `Parasoft` → Get Code, Search `Termius` → Activate → redeem at termius.com

- **TASK-VSDE-006 Atlas/Datadog $500+**:
  https://education.github.com/pack → Sign in GitHub → Claim MongoDB Atlas $500, Datadog, Namecheap, DigitalOcean $200

**After each:** Tell me `004 done` etc. — I run:
```
python -c "update data/tasks.json status DONE" ; git commit -m "vsde 004 DONE" ; git push ; az webapp deploy --src-path host_minimal_v2.zip
```

## 2. gdrive 3rd Backup (2 min, fixes 401 placeholder_token)

Current: `rclone config show` → `gdrive: token = placeholder_token_for_offline_backup` → `rclone lsd gdrive:` → `401 Invalid Credentials`

Steps for your other AI with browser:
```
rclone config
→ n) New remote? No, edit existing `gdrive`
→ Edit `gdrive`? y
→ type `drive`, scope `drive`, `client_id` Enter, `client_secret` Enter
→ Edit advanced? n
→ Use auto config? y  (opens browser → sign in amd949609@gmail.com → Allow)
→ `rclone lsd gdrive:` (should list)
→ `rclone copy data/VSDE_STEROIDS_GUIDE_v2.md gdrive:Sharedall/OsintNeoAi/ --progress`
→ `rclone copy C:\Users\AMD949~1\AppData\Local\Temp\opencode\host_minimal_v2.zip gdrive:Sharedall/OsintNeoAi/backups/repo/`
```
OneDrive: `C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo\` is `Users:RX` only — needs admin `icacls` or copy to `C:\Users\AMD949~1\AppData\Local\Temp\opencode\OneDrive_fallback\` then manual drag.

## 3. Azure ExternalGit Re-enable (1 min, makes `git push` auto-host)

Currently hosted via `OneDeploy` zip (works 200) but `ExternalGit https://github.com/Tonypost949/OsintNeoAi.git main` is sync-locked (`a9e85498a3` 08:52 stuck).

For other AI:
```
az webapp deployment source show --name osintneoai-app-949 --resource-group neoai-rg
az webapp deployment source sync --name osintneoai-app-949 --resource-group neoai-rg
# if 409 Conflict → az webapp restart + wait 60s + sync again
```

## What Autonomous AI Already Did (no user needed)

- Local: `python OSINTNeoAiCLI.py` → `:5052` 200 verified `200` for `/ /syncfusion /tasks /api/tasks`
- Hosted: `host_minimal_v2.zip` 73 files 1.1MB → `az webapp deploy` → `https://osintneoai-app-949.azurewebsites.net/syncfusion` 200 36153 `registerLicense` + `vsdeData` toggle
- MCP: `.vscode/mcp.json:3` `{"servers":{"azure-devops":{"type":"http","url":"https://mcp.dev.azure.com/anthonydimarcello"}}}` `data/azure_devops_mcp_config.json:2` org `anthonydimarcello` project `osintneoai`
- GitHub: `fa05dc6` `8fd32d3` `a9e8549` pushed, `data/tasks.json:38` 53 tasks, `TASK-VSDE-003:DONE` via MCP
- Directions: `data/AI_DIRECTIONS_STEROIDS_HOST_MCP.md:1` + this file

## Hand this to other AI:

```
Read C:\OsintNeoAi\data\MANUAL_STEPS_OTHER_AI_AND_USER.md and C:\OsintNeoAi\data\AI_DIRECTIONS_STEROIDS_HOST_MCP.md, do only browser steps 1 and 2, then mark data/tasks.json DONE and redeploy host_minimal_v2.zip.
```

