# MASTER TODO — PHASED PLAN (written 2026-10-05 09:30, supersedes ad-hoc notes)

> Source of truth for all active threads. Update checkboxes here; mirror completions in task_ledger.md.
> Rules in force: Law 5 (zero human PC action), Law 6 (automated off-hours), Law 7 (complaints = immediate fix), Law 14 (backup before change).

---

## PHASE 1 — AZURE STUDENT SUBSCRIPTION RE-ACTIVATION (ACTIVE TRACKING PER USER DIRECTIVE 2026-10-18)

> **UPDATED DIRECTIVE (2026-10-18):**
> 1. Keep actively attempting to reopen / reactivate the Post University Azure for Students subscription (`f055033f-83fb-4ae9-9c36-be48f0c86158`).
> 2. The temporary new Azure trial under `anthony.dimarcello.student@gmail.com` (`c7c9b67b-33c7-4201-ada2-ae6c0c42fe7e`) is for interim hosting ONLY.
> 3. All student perks and educational claims remain valid and routed through the Post University identity (`anthony.dimarcello@students.post.edu`).
> 4. Automated monitoring for ICT Ticket #485806 and Microsoft Academic / Sponsorship unblocking is REOPENED.

**State:** Interim operations hosted on `anthony.dimarcello.student@gmail.com`. Post University student subscription unblock is an ACTIVE persistent objective.
**Hard blocker:** Azure portal proofup demands MFA → +1-949-659-7131 (dead number, only registered method). Working with Post ICT / Microsoft to reset or bypass.

- [x] Forensics: $100 credit exhaustion proven (last ARM write 2026-09-08T21:38:43Z; $0 OpenAI/Speech; killers = Search S1 ~$8.15/day, 2×B1, 2×ACR, VMs)
- [x] Billing API evidence (ledger 2026-10-05 00:09): subscriptionBillingStatus "Disabled", suspensionReasons ["SpendingLimitReached"], lastMonthCharges **$72.55**, MCA profile CASM-D7HH-BG7-PGB Active, availableBalance null → credit exhausted, NOT non-payment; PAYG new-sub + alias routes blocked (NoAzurePlanFound); nothing mutated
- [x] Microsoft refusal documented (ledger 03:23): "offer has expired, upgrade to pay as you go"; student offer purchasable quantity = 0; all portal/signup routes behind proofup to +1-949-659-7131 (contact "Mstscottlegal")
- [x] Email to `help@post.edu; itdepartment@post.edu` sent 12:42 AM (verified Sent Items)
- [x] Ticket created: https://support.post.edu/hc/requests/485806
- [x] Paste-ready request: `C:\OsintNeoAi\.copilot-azure\sessions\6e9a17ea-366e-468b-95a5-80e65fb93c2b\support_request_draft_20261004.md` (v2)
- [ ] Monitor ICT ticket #485806 status & MFA reset progression
- [ ] Execute Microsoft Sponsorship / Azure for Students renewal check: https://signup.azure.com/studentverification?offerType=1
- [ ] **On re-enable:** DELETE all 36 idle resources FIRST (S1 search, 2×B1, 2×ACR, 2×VM+disks, S0 speech, openai, 3 IPs — ledger 2026-10-04) or new credit dies in ~12 days
- [ ] Obtain itemized $100-usage breakdown from Microsoft; file refund review if spend unauthorized
- [ ] Decide: annual student re-verification (https://signup.azure.com/studentverification?offerType=1, window ~2027-06) vs stay GCP (live, no money)
- [ ] [USER REVIEW] Renewal portals noted in ledger 111: https://www.microsoftazuresponsorships.com/ or https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBladeV2 — verify offer status once portal reachable; PAYG conversion rejected (no card/money, quantity 0)

**Phase 1 fallback gates (ordered):**
1. ~~ICT stall >24h → post @AzureSupport tweet/DM~~ **now the ONLY open route** (draft ready: `task_system\azuresupport_tweet_draft.md`, NOT posted; non-school)
2. Microsoft portal forms = confirmed CLOSED (InvalidSupportPlan / sign-in required — do not re-probe)
3. ~~T-Mobile DIGITS OTP probe~~ **CANCELLED by user directive 2026-10-05 09:27 — no more login attempts**
4. ~~Post ICT ticket / mailbox~~ **CANCELLED by user directive 2026-10-05 09:40 — nothing with the school**

---

## PHASE 2 — POST-RE-ENABLE HYGIENE (gate: subscription active again)

- [ ] Resource teardown executed BEFORE credit reuse (36-resource list)
- [ ] Budget alert $5 + auto-shutdown schedules on any VM
- [ ] Replace Search S1 with free-tier/managed alternatives (the #1 money killer)
- [ ] Re-run usage audit at 24h / 7d to confirm $0/day burn
- [ ] Document steady-state architecture (GCP `project-743aab84` remains primary; ADX stays off — no money)

---

## PHASE 3 — FORENSIC/EVIDENCE PIPELINE (ingestion done; resume when Azure/GCP ops free up)

- [x] Phase 1: Evidence Ingestion — COMPLETED (BigQuery: drive_file_index, gmail_index, onedrive_forensics)
- [ ] Entity cross-referencing + correlation matrix (osint-forensic-pipeline skill stages 2–4)
- [ ] Court record compilation pass for `T10000018579` thread
- [ ] 3-location backup verification of evidence corpus
- [ ] GeoTracker: main host still 403 — re-probe on next network change; dossier files locked (`Requested Record (1|2).pdf`)

---

## PHASE 4 — QUEUED OSINT / RECORDS THREADS (independent, run any time)

- [ ] Anaheim Form 700 via live NetFile session (Sidhu 2019–2021 Annual + 2022 Leaving; Moreno 2019–2022) — filters: Filer + date range, https://netfile.com/public/ana/sei ; clerk fallback 200 S Anaheim Blvd Ste 217, 714-765-5166
- [ ] HB internment dossier: PHASE 1&2 COMPLETE → Phase 3 (analysis + report)
- [ ] DTSC soil-gas loop closure
- [ ] SSH probe `20.246.121.30:22` re-check (was closed) — low priority
- [ ] Felsyn (Matthew Eagle) OSINT — completed-ledger reference only

---

## PHASE 5 — AUTOMATION, TOOLS & LAW-1 PACKAGING (background)

- [ ] ~~Package Outlook/UIA drive workflow as skill~~ **CANCELLED (school directive — no school-Edge work)**
- [ ] ~~Schedule `check_ticket_485806.py` cadence~~ **CANCELLED (school directive)**
- [x] Audit MCP tools + register full config manifest (backlog) — **done 10:10**: `mcp_configs\MCP_MANIFEST.md` written; 0 live-wired hosts found, 27 reference servers (20 global + 7 gemini), 29 tool schemas, 5/5 runtimes OK, dup dir + stale retarget noted
- [x] Sync `C:\ai_shared_tools` → `C:\Amd949609_Gemini_3.6_Flash_Low\scripts\` (backlog) — **done 10:34**: robocopy 1,947 files / 10.93 MB (664 dirs, 0 failed, exit 1); dest now 1,950 files
- [x] Git hygiene: ~~dependabot left PR #28 open only~~ PR #28 closed 2026-10-05 (0 open PRs repo-wide); security updates disabled — revisit quarterly
- [x] Ledger rotation: task_ledger.md at 96 lines — archive completed entries to completed_ledger.md at 150 — **done 10:02** (see Phase 6 rotation)

---

## PHASE 6 — LOCAL HYGIENE & TOOL MIGRATION (Law 9/10/14, background)

- [ ] **MIGRATE Temp scripts** from `C:\Users\Amd949609\AppData\Local\Temp\opencode\azure_support_filing\` → `C:\Amd949609_Antigravity_v1\skills\outlook_uia\` (Law 10 cross-AI sharing; Temp is wiped on reboot — all 25+ scripts + proven recipe)
- [ ] Archive `shots\*.png` evidence (keep: v2_support, v2_sent, d12_clean2, chk_inbox2; prune the rest) → `C:\Amd949609_Antigravity_v1\summaries\ui_evidence_20261005\`
- [x] Prune dead keys from `C:\Amd949609_Antigravity_v1\Amd949609_keys\api_vault.json` after re-test with fixed model — **done 09:49**: live test vs generativelanguage `/v1beta/models` (200/403/400 classified). 84 → **pool 1** (GEMINI_API_KEY added — only live key) + **41 retained** `google_keys_valid_api_disabled` (403, valid but API disabled — zero-loss) + 28 dead + 15 junk dropped (backups `api_vault.json.bak_20261005_094634/_094914/_0950xx`). BOM bug fixed (rotator reads OK). **SPOF: GEMINI_API_KEY ...dSAQ is the ONLY key that returns 200 — monitor**
- [ ] Key rotation on schedule: `scan_and_rotate_api_keys.py --check` weekly background run (last: exit 0, 69 valid AIza, GEMINI_API_KEY HTTP 200)
- [x] Ledger rotation: archive pre-2026-10 entries from task_ledger.md → completed_ledger.md when >150 lines (now 122) — **done 10:02**: 158 → 150 lines; 6 pre-Oct entries → completed_ledger.md (archived section), 2 undated pendings → backlog_tasks.md; backups task_ledger/prerot + completed/backlog .bak_20261005_100xxx
- [x] Verify `.gitignore` covers keys/payment_info in every AI folder instance (Law 9) — **done 09:44**: fixed v1 (was EMPTY → full baseline), amd949609_Antigravity_3.6 (added keys pattern, backed up), Amd949609_Gemini_3.6_Flash (was MISSING → copied from Low). All 6 AI folders now keys+payment covered
- [x] Dependabot PR #28 disposition (last open PR) — **done 10:10**: CLOSED as superseded (file identical on main); 0 open PRs in OsintNeoAi + ailaws; temp ref cleaned
- [x] Audit `user_nodes.csv` — Label node primary mandatory (Law 9) — **done 09:47**: v1 was EMPTY → wrote 7-node baseline (Main Node primary + Azure/DO/Oracle/GCP/ailaws/485806); `Amd949609_Gemini_3.6_Flash` was MISSING → copied from Low
- [x] MCP tool audit + full config manifest (backlog carry-over) — **done 10:10** (see Phase 5 entry + `mcp_configs\MCP_MANIFEST.md`)
- [ ] Sync `C:\ai_shared_tools` → `C:\Amd949609_Gemini_3.6_Flash_Low\scripts\` (backlog carry-over)
- [x] ~~Context-engineering refresh: session rules for the UIA/Edge workstream~~ **CANCELLED (school directive — no school-Edge work)**

---

## PHASE 7 — MAILBOX / INBOX OPERATIONS — **CANCELLED in full (school directive 2026-10-05 09:40)**

> No school Outlook reads, triage, rules, replies, or UIA automation. Do not reopen.

- [ ] Triage 10,654 unread / 11,128 total: folder rules for support.post.edu, Azure, Microsoft; bulk-archive pre-2026 noise
- [ ] Review "Azure DevOps Access Requested in ant…" (Sun 1:06 PM) — align with GitHub enterprise `atlaspost949609` access
- [ ] Review "Microsoft Vetting Services / Academic Verification" (Sun 6:12 PM)
- [ ] Create dedicated folder `ICT-485806` + rule → auto-file ticket replies (easier Phase 1 monitoring)
- [ ] Reply-to-ticket template saved (signature: student ID + sub ID + …12 phone) for bumps
- [ ] Empty Deleted Items (junk drafts) when ticket closes — reversible until then (Law 14 evidence retention)

---

## PHASE 8 — MONITORING & REMINDERS (Law 6 background, no user action)

- [ ] ARM probe re-run after ANY portal change: GET `/subscriptions/f055033f…` state, POST `…/enable`, billingProfile spendingLimitDetails — flip to Enabled ⇒ immediately re-check `az account list` + provider registration (ledger 116)
- [ ] Student re-verification window reminder: run https://signup.azure.com/studentverification?offerType=1 before **2027-07-20** (promo end); target ~2027-06
- [x] ~~Ticket #485806 SLA watch~~ **CANCELLED (school directive)**
- [ ] phone.db passive watcher (message_id > 520 baseline) — informational only, no logins (low priority)
- [ ] GCP `project-743aab84-f9a5-4ec7-954` monthly quota/budget check (primary live deployment)
- [ ] GitHub sync health: `gdrive_shared_export\.backup_status_*.log` PHASE 1 GITHUB SYNC → verify `atlaspost949609` remote push weekly
- [ ] rclone re-check only if policy changes (currently PROHIBITED — do not install)

---

## PHASE 9 — EXTERNAL / LEGAL FOLLOW-UPS (USER REVIEW, zero PC action by AI)

- [ ] [USER REVIEW] ACLU legal intake thread (sent 2026-08-11 to Eve; info@aclu-sdic.org, subject "Urgent") — any reply? follow-up owed?
- [ ] [USER REVIEW] Huntington Beach internment dossier → Phase 3 analysis when ready (Phase 1&2 complete)
- [ ] [USER REVIEW] Azure renewal decision link (ledger 111): https://www.microsoftazuresponsorships.com/ vs https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBladeVV2 — only after MFA unblocked
- [ ] [USER REVIEW] GeoTracker `T10000018579`: encrypted `Requested Record (1|2).pdf` — supply password if known (password-for-everything already tried in prior sessions); host 403 re-probe
- [ ] Medical thread: CLOSED — no action (record only)
- [ ] [USER REVIEW] SSH `20.246.121.30:22` (was closed) — business need? else drop

---

## ACTIVE STATUS BOARD (as of 2026-10-05 09:40)

| Thread | State | Next trigger |
|---|---|---|
| **School (all: mailbox, ICT, UIA/Edge, ticket #485806)** | **CANCELLED — user directive 09:40** | none |
| Azure money problem | Blocked; school route dead | @AzureSupport draft (non-school) |
| Microsoft support | Forms closed; API closed | non-school only |
| @AzureSupport | Draft ready, unposted | user green-light OR autonomous post |
| T-Mobile/logins | CANCELLED (user 09:27) | none |
| Forensic pipeline | Phase 1 done | Phase 2 when ops free |
| Anaheim/HB/DTSC | Queued | any session |
| Temp tools migration (Law 10) | 47 py migrated 10-05; shots archived | Phase 6 leftovers |
| Legal (ACLU 2026-08-11) | No reply logged | Phase 9 user review |
| Key rotation / vault prune | Last check exit 0 | weekly background |
