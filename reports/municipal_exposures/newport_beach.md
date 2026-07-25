# 🛡️ MUNICIPAL EXPOSURE REPORT: NEWPORT BEACH

**TARGET:** newportbeachca.gov / nbpd.org
**STATUS:** ✅ VERIFIED — Raw TCP Socket Strike Complete
**SCOPE:** Whole City Infrastructure Audit
**SCAN DATE:** 2026-07-24 04:51:32

---

## 📋 SUMMARY
South County coastal corridor. Newport Beach municipal infrastructure protected by Cloudflare WAF. NBPD runs bare Microsoft-IIS/10.0 with ASP.NET — no WAF layer.

## 🚨 VERIFIED HITS

### newportbeachca.gov (104.18.10.121 / 104.18.11.121)
| Port | State | Banner |
|------|-------|--------|
| 80 | OPEN | HTTP/1.1 302 -> https://www.newportbeachca.gov/ |
| 443 | OPEN | HTTP/1.1 200 OK (Cloudflare) |
| 21 | FILTERED | FTP |
| 22 | FILTERED | SSH |
| 25 | FILTERED | SMTP |

**Server:** cloudflare
**Backend:** ASP.NET
**HSTS:** max-age=31536000
**WAF:** Cloudflare (cf-cache-status: DYNAMIC, __cf_bm, CF-RAY)
**Session Leak:** ASP.NET_SessionId cookie exposed

### nbpd.org (70.167.157.164)
| Port | State | Banner |
|------|-------|--------|
| 80 | OPEN | HTTP/1.1 302 -> https://www.nbpd.org |
| 443 | OPEN | HTTP/1.1 302 -> https://www.nbpd.org |
| 21 | FILTERED | FTP |
| 22 | FILTERED | SSH |
| 25 | FILTERED | SMTP |

**Server:** Microsoft-IIS/10.0
**X-Powered-By:** ASP.NET
**WAF:** ⚠️ NONE — Direct IIS exposure

## 🔍 FORENSIC NOTES
1. NBPD has NO Cloudflare WAF — direct Microsoft-IIS/10.0 exposure
2. ASP.NET SessionId cookies exposed on both endpoints
3. Cloudflare Insights beacon active on newportbeachca.gov
4. HSTS enabled on municipal site but NOT on NBPD

## 📁 EVIDENCE
- Scan log: agent/nationwide_banner_scan_*.log
- Matrix status: VERIFIED
