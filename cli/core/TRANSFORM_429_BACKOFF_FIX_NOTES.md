# Repair: HTTP 429 Rate Limit — Exponential Backoff in `cli/core/transforms.py`

**Date**: 2026-11-02
**Prompt handled**: "Repair failing transform and handle HTTP 429 rate limit with exponential backoff"
**Simulated connector exception**: `HTTP 429 rate limit exceeded` (see `cli/core/multi_engine.py` Stage 8, opencode self-healing)

## What Was Broken

Every transform in `cli/core/transforms.py` called `requests.get/post/head` directly.
When a connector answered **HTTP 429**, the response fell through to a generic
`except`/status check and the transform returned `[]` — i.e. it silently failed.
No retry, no backoff, no `Retry-After` handling. `EmailToHIBP` even returned a
static "retry in 60s" message instead of retrying.

## What Was Changed (file: `cli/core/transforms.py`)

1. **New shared helper `http_request(method, url, ...)`**
   - Retries on `429, 502, 503, 504`.
   - **Exponential backoff**: `base_delay * 2**attempt` (default base 1s → 1, 2, 4, 8s),
     **±25% jitter**, hard cap **60s** (`MAX_BACKOFF_DELAY`).
   - **Honours `Retry-After`** header (integer seconds *or* HTTP-date format).
   - Default `max_retries = 4` (5 total attempts), then returns the last response
     so the caller decides how to report the failure.
2. **All HTTP call sites routed through the helper**:
   `EmailToSocialProfile` (HEAD), `DomainToVirusTotal`, `DomainToWHOIS` (RDAP),
   `DomainToSSLCert` (crt.sh), `EmailToHIBP` (+ k-Anonymity ping),
   `DomainToDNS` (Google DoH), `IPToGeoLocation` (ip-api + ipinfo.io),
   `DomainToReputation` (Safe Browsing POST, URLHaus POST, AbuseIPDB GET),
   `WebSearch` (Bing API, Bing scrape, Brave API, Google CSE).
3. **`IPToShodanInfo`**: `shodan.APIError` rate-limit messages ("429"/"rate limit")
   are retried with the same `_backoff_delay()` schedule.
4. **`EmailToHIBP`**: after exhausted backoff, returns an explicit
   "still rate limited after N backoff retries" record instead of a fake fixed advice.
5. **`DomainToReputation` (Google Safe Browsing)**: an exhausted 429 now returns
   `[GSB] Rate limited after backoff — retry later` — it can **never** report
   a false `[GSB] Clean` on a rate-limited response.

## How To Verify

```bash
cd cli
python -m py_compile core/transforms.py
python test_backoff_429.py
```

`test_backoff_429.py` mocks `requests.request`/`time.sleep` (no live network):
429→429→200 recovery, persistent-429 exhaustion (1+retries attempts, exponential
sleep sequence), jitter/cap bounds, non-retryable 404 passthrough, and an
end-to-end `DomainToVirusTotal` run recovering from two 429s.
All 5 tests pass as of this commit.

## Backup / Resurrection State (per AGENTS.md)

| Location | State |
|---|---|
| GitHub | ✅ `rico-report-2026` @ `f0beb30` (pre-change backup commit `6fc5224`), plus safety branch `backup/429-backoff-20261102` @ `f0beb30`. **`main` has diverged remotely** — a non-force push was rejected; owner must consolidate (`git pull` then push). Never force-pushed. |
| Local PC (C:\ OneDrive) | ✅ Via rclone `onedrive:` remote → `Documents/OsintNeoAi/backups/repo/pre_429_backoff_20261102_104603/` and `post_429_backoff_20261102_110100/` (originals preserved, not overwritten) |
| On-device offline copy | ✅ `.backup_20261102_104603/` and `.backup_20261102_110100/` in repo root |
| Sharedall Google Drive | ❌ **BLOCKED**: rclone `gdrive:` remote has an empty OAuth token. Restore with: `rclone config reconnect gdrive:` (interactive — open the printed URL, paste the verification code), then: `rclone copy .backup_20261102_104603 gdrive:Sharedall/OsintNeoAi/backups/pre_429_backoff_20261102_104603` and `rclone copy .backup_20261102_110100 gdrive:Sharedall/OsintNeoAi/backups/post_429_backoff_20261102_110100` |

## For Future Agents

- Do not replace `http_request()` with raw `requests.*` calls — every new
  transform should use it (or another Retry-After-aware wrapper).
- Constants to tune: `RETRYABLE_STATUS_CODES`, `DEFAULT_MAX_RETRIES`,
  `DEFAULT_BASE_DELAY`, `MAX_BACKOFF_DELAY`, `BACKOFF_JITTER` (top of file).
- GitHub auth on this device: the `origin` remote embeds a **stale PAT**; push with
  `git -c credential.helper= push "https://x-access-token:$(gh auth token)@github.com/Tonypost949/OsintNeoAi.git" <branch>`.
- Nothing was deleted: the pre-fix file content lives in git history (`6fc5224`),
  both `.backup_*` folders, and both OneDrive backup folders.
