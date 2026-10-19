# ⚠ PUSH-SYNC HAZARD — do NOT run sync_opencode_vm.sh from the PC anymore

**Date:** 2026-10-19 (00:40 UTC)
**Status:** PC->VM push sync RETIRED. VM DB is authoritative.

## What changed

On 2026-10-19 ~00:04 UTC the OpenCode agent session itself migrated onto
`vm-osintneoai-01` (20.127.235.165). This session's parent process is
`opencode.exe serve --service` running ON the VM, OpenCode **v2.0.32**
(`/usr/local/bin/opencode` -> `@opencode/cli/bin/opencode.exe`), inside tmux
session `oc`. The PC window is only a thin `ssh -tt` pipe into that tmux.

## The hazard

`/home/osintneoai/tools/sync_opencode_vm.sh` (on the Kali WSL PC) was built to
push PC state -> VM with `rsync --delete` on `.local/share/opencode`. Conversation
history created **after 2026-10-19T00:03:35Z** exists only on the VM. Running the
old push script now would:

1. kill the live tmux `oc` session on the VM,
2. replace the live VM DB with the stale PC copy,
3. destroy every message in the fork after the last PC-side snapshot.

## Required action when PC access is next available

1. Rename the script on the PC: `mv ~/tools/sync_opencode_vm.sh ~/tools/sync_opencode_vm.sh.retired_push_sync`
2. If running opencode locally on the PC is ever needed again, build the REVERSE
   direction (VM -> PC pull) using the same sqlite-backup-API snapshot method,
   never `--delete` against the VM.
3. Mirror this file to `C:\Amd949609_Antigravity_v1\tools\` per Law 15.

## Canonical locations (as of 2026-10-19)

| Item | Authoritative location |
|---|---|
| Session DB | `/home/osintneoai/.local/share/opencode/opencode.db` on vm-01 |
| Engine | `/usr/local/lib/node_modules/@opencode/cli` (v2.0.32) on vm-01 |
| Config | `/home/osintneoai/.config/opencode/opencode.jsonc` on vm-01 |
| Task system | `/home/osintneoai/tools/task_system/` on vm-01 |
| Old v1.18.34 binary | `~/.opencode/bin/opencode` on both hosts — kept unused (zero deletion), PATH order fixed so it never wins |
