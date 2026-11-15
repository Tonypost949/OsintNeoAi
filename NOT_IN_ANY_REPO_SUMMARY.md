# Not-in-any-repo inventory - summary (2026-11-14)

Plain summary. Measured this session by walking ~/workspace file by file (build_inventory.py in this folder). Nothing was moved, deleted, pushed, or uploaded.

## Method and repo-path universe - exactly what was used

- **Universe U1:** every file under ~/workspace/osintneoai-github/ excluding .git - the old big OsintNeoAi checkout @35099d0 (2,713 files materialized in this partial, blob:none clone today; the 2026-11-06 audit counted 12,428 files in that checkout - the difference is un-materialized blobs in the partial clone, named here as a gap, not hidden).
- **Universe U2:** every file under the 20 repo roots in ~/workspace/github-consolidation/<owner>/<repo>/ excluding .git - 19 git clones + txtdjdrop/OSINTNEOAI extracted from its codeload zip (9,636 files).
- **Universe U3 (reused, dated 2026-11-06):** basenames from ~/workspace/backup-drive-audit-2026-11-06/in_old_repo_not_live.csv (4,255 rows) and clean_in-old-not-live.csv (1,368 rows), from the audit that measured the all-branches union of Tonypost949/OsintNeoAi at 15,745 unique paths (20 branches + 2 tags). The audit's own /tmp path lists no longer exist, so U3 adds basenames only.
- Universe total walked: 12,349 files, 7,207 unique basenames, 9,974 unique repo-relative paths across U1+U2.
- **Matching = basename, lowercased** - the same method as the 2026-11-06 audit. Same name does NOT prove same content; generic names (README.md, index.html, package.json) inflate the match count. Content-hash verification was NOT done in this pass.
- **Classification:** a workspace file is (a) `in_local_repo_checkout` if it physically sits inside U1/U2, (b) `basename_match` if its basename is in the universe but it sits outside any checkout, (c) `not_in_any_repo` otherwise.
- **Scope/exclusions from the count itself:** .git internals were not walked; the output folder ~/workspace/repo-unification-2026-11-14/ was excluded to avoid self-reference (it also holds the main agent's Google Tasks import files, created in parallel). Upstream third-party tool clones under ~/workspace/tools/ (55 .git roots found at depth <=4 workspace-wide, most of them tools) were NOT put in the universe - they are other people's repos, not the owner's.
- Earlier the same day the workspace headline was 441,426 files / 46 GB (including .git internals). This pass counts 440,649 files / 49,497,852,570 bytes (~49.5 GB by raw byte sum) under the scope above - the two totals use different scopes, both are stated, neither is hidden.

## Totals

- Workspace files counted: **440,649** (49.50 GB, 49,497,852,570 bytes)
- In a local repo checkout: **12,349**
- Basename-match to a repo path (outside any checkout, content unverified): **29,697**
- **Not in any repo: 398,603 files** - full path+size list: ~/workspace/repo-unification-2026-11-14/not_in_any_repo_files.csv (398,603 rows)
- Per-folder counts and sizes: ~/workspace/repo-unification-2026-11-14/inventory_by_folder.csv (level 1 for all 142 top folders; level 2 for folders with >=500 files - 1,189 data rows)

## Not-in-any-repo, broken down by top folder (top 30 by not-in-repo size)

| Top folder | Files total | Size total | In checkout | Basename match | Not in repo (files) | Not in repo (size) |
|---|---|---|---|---|---|---|
| tools | 375,613 | 16.50 GB | 0 | 26,622 | 348,991 | 14.97 GB |
| dj-drop-staging | 5,879 | 8.91 GB | 0 | 242 | 5,637 | 8.90 GB |
| browser_downloads | 583 | 4.26 GB | 0 | 0 | 583 | 4.26 GB |
| tablet-offload-9185w | 183 | 2.48 GB | 0 | 3 | 180 | 2.48 GB |
| github-sync-osintneoai-internment | 897 | 2.42 GB | 0 | 1 | 896 | 2.42 GB |
| task_system | 311 | 2.02 GB | 0 | 2 | 309 | 2.02 GB |
| github-consolidation | 9,638 | 4.88 GB | 9,636 | 1 | 1 | 1.85 GB |
| knabb-case | 1,467 | 1.02 GB | 0 | 3 | 1,464 | 1.02 GB |
| downloads | 24 | 0.88 GB | 0 | 0 | 24 | 0.88 GB |
| foia-frames | 7,433 | 0.65 GB | 0 | 241 | 7,192 | 0.65 GB |
| hbnc-esa-hunt | 143 | 0.61 GB | 0 | 9 | 134 | 0.60 GB |
| anonymous-tip-2026-11-08 | 529 | 0.51 GB | 0 | 2 | 527 | 0.51 GB |
| .venvs | 4,606 | 0.48 GB | 0 | 241 | 4,365 | 0.48 GB |
| tmp-relocated-2026-11-07 | 443 | 0.42 GB | 0 | 0 | 443 | 0.42 GB |
| .hatch-browser | 2,951 | 0.40 GB | 0 | 1,198 | 1,753 | 0.39 GB |
| ts-spaces | 8,837 | 0.24 GB | 0 | 445 | 8,392 | 0.23 GB |
| ip-pile | 99 | 0.22 GB | 0 | 9 | 90 | 0.22 GB |
| .venv-deliverables | 5,096 | 0.20 GB | 0 | 230 | 4,866 | 0.20 GB |
| goals | 1,478 | 0.17 GB | 0 | 15 | 1,463 | 0.17 GB |
| osintneoai-media-all | 203 | 0.18 GB | 0 | 39 | 164 | 0.17 GB |
| buck-ranch-local-history | 170 | 0.15 GB | 0 | 0 | 170 | 0.15 GB |
| millworks-pull | 124 | 0.15 GB | 0 | 0 | 124 | 0.15 GB |
| dehashed-collection | 104 | 0.14 GB | 0 | 1 | 103 | 0.14 GB |
| mom-videos | 3 | 0.13 GB | 0 | 0 | 3 | 0.13 GB |
| space-versions | 190 | 88.31 MB | 0 | 60 | 130 | 86.93 MB |
| arbitrage-rebuild | 1,185 | 86.67 MB | 0 | 88 | 1,097 | 86.10 MB |
| avatars | 73 | 85.58 MB | 0 | 0 | 73 | 85.58 MB |
| agents | 1,091 | 79.69 MB | 0 | 0 | 1,091 | 79.69 MB |
| transparency-packet | 805 | 73.66 MB | 0 | 46 | 759 | 73.12 MB |
| drive-cleanup | 13 | 70.83 MB | 0 | 0 | 13 | 70.83 MB |

Note: `tools/` dominates the not-in-repo count (348,991 of 398,603 files) - that is installed third-party tooling, venvs and node_modules, most of it re-installable from upstream, not unique owner work. The owner's unique work is concentrated in goals/, task_system/, the case/evidence folders, and the staging/offload folders below it in the table.

## Largest not-in-any-repo files (top 50, path + size only)

1. github-consolidation/txtdjdrop/OSINTNEOAI-main.zip - 1.85 GB (1,845,582,067 bytes)
2. tablet-offload-9185w/Download/APT2024filesfull.zip - 0.95 GB (946,547,130 bytes)
3. task_system/aad_pull/originals/nr-far-tulelake.pdf - 0.68 GB (677,533,878 bytes)
4. task_system/aad_pull/originals/nr-far-poston.pdf - 0.56 GB (555,399,116 bytes)
5. tools/repoghost/.venv/lib/python3.12/site-packages/torch/lib/libtorch_cpu.so - 0.44 GB (440,280,512 bytes)
6. task_system/aad_pull/originals/nr-far-tulelake_jp2.zip - 0.41 GB (412,178,978 bytes)
7. tablet-offload-9185w/Camera/VID_20260507_122647.mp4.tmp - 0.40 GB (403,039,134 bytes)
8. tools/blender/blender-5.2.3.tar.xz - 0.39 GB (385,331,224 bytes)
9. tools/blender/blender-4.2.23-linux-x64.tar.xz - 0.35 GB (350,707,672 bytes)
10. dj-drop-staging/rage-woodstock-99/src/full-concert.mp4 - 0.34 GB (344,156,008 bytes)
11. dj-drop-staging/00-intro/blender-template/universal_intro_282.blend - 0.30 GB (304,576,560 bytes)
12. tmp-relocated-2026-11-07/wcr.csv - 0.29 GB (290,836,480 bytes)
13. tools/opencode/node_modules/@opencode/cli/bin/opencode.exe - 0.25 GB (252,713,136 bytes)
14. tools/opencode/node_modules/.bin/opencode2 - 0.25 GB (252,713,136 bytes)
15. tablet-offload-9185w/Download/Antigravity IDE.tar.gz - 0.24 GB (236,865,493 bytes)
16. downloads/reel-1059569189888658.mp4 - 0.22 GB (224,629,860 bytes)
17. dj-drop-staging/00-intro/blender-template/texfix/clouds.png - 0.21 GB (210,808,929 bytes)
18. tablet-offload-9185w/Download/kimiclaw_1.0.2.apk - 0.20 GB (202,613,318 bytes)
19. tools/vercel-cli/lib/node_modules/vercel/node_modules/@vercel/vc-native-linux-x64/bin/vercel - 0.18 GB (179,375,296 bytes)
20. tablet-offload-9185w/Download/Antigravity.tar.gz.tar - 0.18 GB (179,168,144 bytes)
21. tools/blender/blender-5.2.3-linux-x64/blender - 0.17 GB (174,261,472 bytes)
22. foia-frames/sequence-pulls/cia-readingroom-document-cia-rdp80-00926a001600020001-3.pdf - 0.17 GB (166,954,337 bytes)
23. downloads/DaBaby-Rockstar-Official-mxFstYSbBmc.mp4 - 0.14 GB (140,446,740 bytes)
24. tools/blender/blender-4.2.23-linux-x64/blender - 0.14 GB (139,536,816 bytes)
25. downloads/Lil-Wayne-No-Worries-5z25pGEGBM4.mp4 - 0.14 GB (138,724,549 bytes)
26. tools/blender/blender-4.2.23-linux-x64/lib/libcycles_kernel_oneapi_aot.so - 0.14 GB (137,497,032 bytes)
27. tools/Scrapling/.venv/lib/python3.12/site-packages/playwright/driver/node - 0.13 GB (126,879,696 bytes)
28. tools/Scrapling/.venv/lib/python3.12/site-packages/patchright/driver/node - 0.13 GB (126,879,696 bytes)
29. tools/shadowbroker/backend/venv/lib/python3.12/site-packages/playwright/driver/node - 0.13 GB (126,879,696 bytes)
30. dj-drop-staging/rage-woodstock-99/full/concert.wav - 0.12 GB (124,036,246 bytes)
31. tablet-offload-9185w/Download/com.termux_1021.apk - 0.11 GB (114,920,926 bytes)
32. browser_downloads/sess-956616326/browser-download-20261106T183634.502894476Z-16-T10000018579.20200625.Site_Assessment_Report.pdf - 0.11 GB (108,993,521 bytes)
33. knabb-case/geotracker-T10000018579/EEC_Site_Assessment_FULL_2020-06-25_149pp.pdf - 0.11 GB (108,993,521 bytes)
34. tools/sheepit/jdk-21.0.13+9-jre/lib/modules - 0.10 GB (101,274,197 bytes)
35. tools/shadowbroker/frontend/node_modules/@next/swc-linux-x64-gnu/next-swc.linux-x64-gnu.node - 0.10 GB (100,927,408 bytes)
36. tools/blender/blender-4.2.23-linux-x64/lib/liboslexec.so - 94.21 MB (94,209,440 bytes)
37. tools/blender/blender-4.2.23-linux-x64/lib/liboslexec.so.1.13.7 - 94.21 MB (94,209,440 bytes)
38. tools/blender/blender-4.2.23-linux-x64/lib/liboslexec.so.1.13 - 94.21 MB (94,209,440 bytes)
39. downloads/DaBaby-Rockstar-Cut-Qmzv7BEfFfo.mp4 - 92.21 MB (92,206,174 bytes)
40. tablet-offload-9185w/Camera/VID_20261024_132219.mp4 - 91.25 MB (91,247,016 bytes)
41. tablet-offload-9185w/Download/Orange_County_Administrative_Attacks_and_Toxic_Shelters.m4a - 84.91 MB (84,912,272 bytes)
42. tools/sheepit/jdk-17.0.21+9-jre/lib/modules - 84.74 MB (84,739,407 bytes)
43. tools/blender/blender-5.2.3-linux-x64/5.2/python/lib/libpython3.13.a - 84.18 MB (84,181,888 bytes)
44. tools/blender/blender-5.2.3-linux-x64/5.2/python/lib/python3.13/config-3.13-x86_64-linux-gnu/libpython3.13.a - 84.18 MB (84,181,888 bytes)
45. tablet-offload-9185w/Camera/VID_20261024_125817.mp4 - 82.36 MB (82,364,212 bytes)
46. dj-drop-staging/rage-woodstock-99/asr-venv/lib/python3.12/site-packages/ctranslate2.libs/libctranslate2-a7a60d30.so.4.8.5 - 80.77 MB (80,773,681 bytes)
47. .venvs/fw/lib/python3.12/site-packages/ctranslate2.libs/libctranslate2-42c542ff.so.4.8.4 - 80.68 MB (80,683,337 bytes)
48. tools/blender/blender-5.2.3-linux-x64/lib/libusd_ms.so - 78.74 MB (78,736,808 bytes)
49. tools/blender/blender-4.2.23-linux-x64/lib/libopenvdb.so.11.0.0 - 76.57 MB (76,569,448 bytes)
50. tools/blender/blender-4.2.23-linux-x64/lib/libopenvdb.so.11.0 - 76.57 MB (76,569,448 bytes)

## Excluded from the public export - categories and counts (paths counted, never copied)

Counted workspace-wide by file name/path patterns (no contents read), plus extension and size rules. A file can hit several categories, so these do not add up to a single total.

- Credentials / keys / .env / .ssh / password-named files: **2,643 files, 49.32 MB** - excluded from export/
- Medical-named files (name/path pattern only): **192 files, 60.10 MB** - excluded from export/
- Takeout / mail-archive files (.mbox, takeout paths): **47 files, 1.75 MB** - excluded from export/
- Binary / media / archive / database / office files (by extension: .zip .mp4 .pdf .docx .xlsx .db .exe etc.): **73,043 files, 30.25 GB** - excluded from export/
- Files over 1 MB (over the export's per-file cap): **4,704 files, 42.24 GB** - excluded from export/
- Private family full names: not counted by filename (names appear inside documents, not filenames). Content-checked only on the files actually staged into export/ (TASKS_REDACTED.md and GOALS_INDEX.md), where close-family full names were replaced with relationship labels - see the redaction header in TASKS_REDACTED.md for exact counts. The rest of the workspace was NOT content-scanned for family names in this pass; that is a named gap, and any future public push needs that scan per file.
- Also excluded from export/ by rule, no exceptions: anything under a .git directory, venv/node_modules trees, and the not_in_any_repo_files.csv path list itself (internal working list, not public material).

## Gaps - stores not checked in this pass

- GitHub remote, live: NOT re-fetched repo-by-repo in this pass. The all-branches union figure (15,745 paths) is the 2026-11-06 measurement, reused. Branches/tags that exist only on GitHub and were never fetched into the local checkouts are a gap - the pull that closes it is a fresh all-refs tree listing per repo via the GitHub connector.
- The other Tonypost949 repos (34 total on the account): only the ones with local clones in U1/U2 are in the universe. Repos without a local clone here are a gap, same pull as above.
- Google Drive, Gmail, Google Photos: not checked - they are separate stores, not repo copies; a Drive-vs-repo comparison is a separate pull.
- djdrop (owner's PC) and the D: backup drive: not re-probed this pass; the 2026-11-06 audit of D: is the last measurement and is reused as dated context only.
- Content identity: basename matching only, no hashing - a 'match' may be a different file with the same name, and a renamed copy of a repo file counts as not-in-repo. Hash-level verification is the follow-up pass.
