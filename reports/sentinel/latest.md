# Sentinel Report — 2026-10-05T09:57:25

**Overall: OK**

## Remote VM & Endpoints

| Check | Status | Detail |
|---|---|---|
| osint-free (GCP, always-free e2-micro) | 🟢 up | 16:57:00 up 1 day, 19:59,  0 user,  load average: 0.00, 0.00, 0.00 |
| GCP map server :10000 /health | 🟢 up | HTTP 200 in 216ms |
| Firebase Live Hub | 🟢 up | HTTP 200 in 62ms |
| GitHub Pages GIS (osintneoai.me) | 🟢 up | HTTP 200 in 189ms |

## AI / Cloud Quota

| Check | Status | Detail |
|---|---|---|
| GitHub API (core) | 🟢 ok | 4991/5000 remaining (99.8%), resets 10:25 |
| Gemini API | 🟢 ok | API alive via gemini-3.8-flash (HTTP 200, no ratelimit headers exposed) |
| GCP IN_USE_ADDRESSES | 🟢 ok | usage 0 / limit 4 (100.0% free) |

## Local Services

| Check | Status | Detail |
|---|---|---|
| OSINTNeoAiCLI hub | 🟢 up | 127.0.0.1:5052 listening |
| Map server | 🟢 up | 127.0.0.1:10000 listening |
