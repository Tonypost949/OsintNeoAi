# Sentinel Report — 2026-10-03T14:19:14

**Overall: CRITICAL**

## Remote VM & Endpoints

| Check | Status | Detail |
|---|---|---|
| osintneoai-vm (Azure) | 🔴 down | ssh: connect to host 20.246.121.30 port 22: Connection timed out |
| osint-cloud (GCP) | 🟢 up | 21:18:51 up 21 min,  0 user,  load average: 0.01, 0.03, 0.05 |
| Azure backend :10000 /health | 🔴 down | HTTP None in 10114ms — <urlopen error timed out> |
| Firebase Live Hub | 🟢 up | HTTP 200 in 269ms |
| GitHub Pages GIS (osintneoai.me) | 🟢 up | HTTP 200 in 197ms |

## AI / Cloud Quota

| Check | Status | Detail |
|---|---|---|
| GitHub API (core) | 🟢 ok | 4998/5000 remaining (100.0%), resets 15:13 |
| Gemini API | 🔴 critical | 402 PAYMENT REQUIRED — project has no Gemini quota/billing enabled |
| GCP IN_USE_ADDRESSES | 🟢 ok | usage 0 / limit 4 (100.0% free) |
| Azure account | 🟢 ok | logged in: Azure for Students |
| Azure VMs | 🟡 warn | 2 VM(s): no public IPs |

## Local Services

| Check | Status | Detail |
|---|---|---|
| OSINTNeoAiCLI hub | 🟢 up | 127.0.0.1:5052 listening |
| Map server | 🟢 up | 127.0.0.1:10000 listening |
