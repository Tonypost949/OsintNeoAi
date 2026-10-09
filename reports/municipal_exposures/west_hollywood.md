# 🛡️ MUNICIPAL EXPOSURE REPORT: WEST HOLLYWOOD

**TARGET:** weho.org / www.weho.org (City of West Hollywood)
**STATUS:** ✅ VERIFIED — Raw TCP Socket Strike Complete
**SCOPE:** Municipal Perimeter Audit
**SCAN DATE:** 2026-10-08 22:28:43 (local) / 2026-10-09T05:28Z
**RESOLVED IP:** 135.84.124.41

---

## 📋 SUMMARY
West Hollywood apex domain weho.org resolves to 135.84.124.41 — the identical IP
address serving costamesaca.gov. This confirms the shared municipal hosting
cluster hypothesized in the Costa Mesa audit. The apex host runs a direct
Microsoft-IIS/10.0 instance with no WAF layer; the www subdomain sits behind
Akamai (AkamaiGHost).

## 🚨 VERIFIED HITS

### weho.org (135.84.124.41)
| Port | State | Banner |
|------|-------|--------|
| 80 | OPEN | HTTP/1.1 200 OK — Server: Microsoft-IIS/10.0, Content-Length: 703, Last-Modified: Mon, 11 May 2026 09:44:35 GMT |
| 443 | FILTERED | — |

**Server:** Microsoft-IIS/10.0
**WAF:** ⚠️ NONE on apex — direct IIS exposure
**Shared infrastructure:** 135.84.124.41 also serves costamesaca.gov

### www.weho.org
| Port | State | Banner |
|------|-------|--------|
| 80 | OPEN | HTTP/1.0 400 Bad Request — Server: AkamaiGHost (bare HTTP/1.0 HEAD rejected by CDN) |
| 443 | FILTERED | — |
| 21 / 22 / 25 | FILTERED | — |

**WAF:** AkamaiGHost present on www subdomain only

## 🔍 FORENSIC NOTES
1. **Shared hosting cluster confirmed:** 135.84.124.41 hosts both weho.org and costamesaca.gov — cross-jurisdictional single point of failure/compromise
2. Apex host exposes Microsoft-IIS/10.0 directly (no CDN/WAF on port 80)
3. www subdomain is Akamai-fronted — inconsistent WAF coverage across the same organization's own domains
4. FTP/SSH/SMTP filtered on www — basic port hygiene in place
5. Last-Modified stamp on apex response: 2026-05-11 — static stub content
6. 443 filtered from this vantage point (TLS may be restricted to CDN/allowlist)

## 📁 EVIDENCE
- Scan logs: C:\OsintNeoAi\nationwide_banner_scan_1791523723.log (apex), C:\OsintNeoAi\nationwide_banner_scan_1791523759.log (www)
- Chain of custody: FEDERAL_SUBMISSION/artifacts_log.csv → ART-006 (report), ART-008 (socket strike)
- Matrix status: VERIFIED
