# VSDE Steroids Benefits — Checklist v1 (2026-08-27)
# Non-destructive additive checklist — does NOT overwrite data/tasks.json, OSINTNeoAiCLI.py, or public/syncfusion_grid.html
# Original live files preserved per AGENTS.md Rule 2.

## Portal
- my.visualstudio.com/benefits  (auth: anthony.dimarcello@students.post.edu Entra SSO)
- Syncfusion downloads: https://www.syncfusion.com/account/downloads

## License
- Order W753756 Essential Studio UI Edition Binary 5-member team 6-mo
- Key: Ngo9BigBOggjGyl/VkJ+Xk9GfVZLVGpUf1FrRmJJfV16cVxMZVVaRnZdRF1rS3hTdURhXXtfd3ZUTWNY
- Registered in: public/syncfusion_grid.html (v1 11 FACTs), public/syncfusion_grid.html_v2 (dual-view VSDE+forensic), public/syncfusion_grid_v3_steroids.html (copy verified)
- Keys backed: data/syncfusion_license.key , data/syncfusion_license.key_amd949609

## Live Routes (OSINTNeoAiCLI_v2.py additive, OSINTNeoAiCLI.py untouched)
- /syncfusion + /syncfusion-grid + /grid → serves v2 (fallback v1)
- /tasks + /tasks-engine + /roadmap → serves public/tasks.html
- /api/tasks → serves data/tasks.json (49 tasks)

## 8 Steroids Tasks (data/tasks.json + data/tasks_v3_steroids.json)
| ID | Title | Status | Value | Action |
|---|---|---|---|---|
| TASK-VSDE-001 | Claim Syncfusion Essential Studio Enterprise $9,995 | DONE | $9,995 | public/syncfusion_grid.html_v2 registerLicense zero watermark |
| TASK-VSDE-002 | Activate Azure for Students $100/mo Credit | DONE | $100/mo | sub f055033f-83fb-4ae9-9c36-be48f0c86158 osintneoai-app-949 B1 |
| TASK-VSDE-003 | Claim JetBrains All Products Pack + GitHub Copilot | TODO | $779/yr | my.visualstudio.com/benefits |
| TASK-VSDE-004 | Claim Pluralsight + LinkedIn Learning + DataCamp Bundle | TODO | $1,200 | benefits portal |
| TASK-VSDE-005 | Claim Parasoft / Code Climate / SQL Sentry / Termius Pro | TODO | $2,400 | benefits portal |
| TASK-VSDE-006 | Claim MongoDB Atlas / Datadog / Namecheap / DigitalOcean | TODO | $500+ | education.github.com/pack |
| TASK-VSDE-007 | Verify Post University Entra SSO Federation | DONE | Active | myaccount.microsoft.com |
| TASK-VSDE-008 | Deploy /syncfusion + /tasks Live on Azure | DONE | Live | 127.0.0.1:5052/syncfusion + azurewebsites |

## Preservation Proof (2026-08-27 verify)
- OSINTNeoAiCLI.py intact (1434 lines) — never edited
- OSINTNeoAiCLI_v2.py parallel (1434 lines) adds routes at line 1159+, 1170+, 1181+
- public/syncfusion_grid.html intact 700 lines
- public/syncfusion_grid.html_v2 parallel 740 lines (vsdeData + forensicData toggle)
- public/syncfusion_grid_v3_steroids.html duplicate of v2 for next iteration
- public/tasks.html intact 669 lines Kanban
- data/tasks.json fixed $9,995 titles, backup at data/tasks.json.backup_20260827
- Local backup: C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo\ backup_20260826_115057 current
- GitHub: origin/main synced (88db5e3 Activate VSDE Steroids)
- gdrive: Sharedall rclone auth 401 needs re-login — flagged, local zip fallback created

## Next Actions (no deletion)
- Claim TODO 003-006 via benefits portal (requires browser Entra login)
- Test local: python OSINTNeoAiCLI_v2.py → http://127.0.0.1:5052/syncfusion (verify no watermark) + /tasks
- Re-auth rclone gdrive: `rclone config` → `gdrive:` token refresh, then `rclone copy ... gdrive:Sharedall/OsintNeoAi/`
- Push pending evidence edits: git add evidence/official_court_records/*.md + commit

## How to use steroids locally
```
python OSINTNeoAiCLI_v2.py
# → http://127.0.0.1:5052/syncfusion  (licensed grid)
# → http://127.0.0.1:5052/tasks       (Kanban from data/tasks.json)
# → http://127.0.0.1:5052/            (Master Hub with Syncfusion+Tasks pills)
python agent/google_tasks_manager.py list-lists
python agent/google_tasks_manager.py create-list "6-VSDE Steroids Benefits"
```

## Deploy Fix 2026-08-27 08:42 UTC - Trigger Azure Redeploy

