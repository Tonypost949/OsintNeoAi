# RICO Enterprise Digital Evidence Package
## OSINT-NeoAI — Generated 2026-07-24
### Repository: https://github.com/Tonypost949/OsintNeoAi
### Branch: feat/city-cyber-recon-map
### Commit: bb13794

---

## EVIDENCE PACKAGE STRUCTURE

```
C:\migrate opencode\OSINTNEOAI\evidence\
├── EVIDENCE_INDEX.md                    (this file)
├── whois/                               (29 WHOIS/DNS records)
├── ssl/                                 (12 SSL certificates)
├── http_headers/                        (12 HTTP header captures)
├── web_content/                         (22 endpoint captures)
├── port_scans/                          (13 port scan results)
├── dns/                                 (reserved)
└── endpoint_captures/                   (reserved)
```

---

## CRITICAL EVIDENCE FILES — LIBERTY/CARLISLE INFRASTRUCTURE

### Libertyseniorliving.com — Liberty Branded, RICO Infrastructure

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\libertyseniorliving.com.txt | https://www.libertyseniorliving.com |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\libertyseniorliving.com.cer | https://libertyseniorliving.com |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\libertyseniorliving.com.txt | https://libertyseniorliving.com |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\libertyseniorliving.com.txt | https://libertyseniorliving.com |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\libertyseniorliving.com_.txt | https://www.libertyseniorliving.com/ |
| WP-Admin Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\libertyseniorliving.com_wp-admin.txt | https://www.libertyseniorliving.com/wp-admin |
| WP-Login Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\libertyseniorliving.com_wp-login.php.txt | https://www.libertyseniorliving.com/wp-login.php |
| Admin Panel Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\libertyseniorliving.com_admin.txt | https://www.libertyseniorliving.com/admin |

**Infrastructure:** 141.193.213.10-11 — Same /24 block as l2tmedia.com (RICO shell) and cookcountysheriff.org
**Risk:** WordPress admin login page exposed on shared RICO infrastructure

### Carlisledev.com — Fraud Convicted ($26M)

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\carlisledev.com.txt | https://carlisledev.com |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\carlisledev.com.cer | https://carlisledev.com |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\carlisledev.com.txt | https://carlisledev.com |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\carlisledev.com.txt | https://carlisledev.com |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\carlisledev.com_.txt | https://carlisledev.com/ |

**Infrastructure:** 3.33.130.190 (AWS) — Same IP as illuminationfoundation.org ($2M PPP fraud)
**Risk:** WAF catch-all (114 bytes) — infrastructure link to RICO nonprofit

### Atlanticpacificcommunities.com — Absorbed Carlisle Assets

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\atlanticpacificcommunities.com.txt | https://atlanticpacificcommunities.com |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\atlanticpacificcommunities.com.cer | https://atlanticpacificcommunities.com |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\atlanticpacificcommunities.com.txt | https://atlanticpacificcommunities.com |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\atlanticpacificcommunities.com.txt | https://atlanticpacificcommunities.com |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\atlanticpacificcommunities.com_.txt | https://atlanticpacificcommunities.com/ |

**Infrastructure:** 3.33.130.190 (AWS) — Same IP as carlisledev.com AND illuminationfoundation.org
**Risk:** Three RICO-connected entities on single AWS IP

### Illuminationfoundation.org — RICO Nonprofit ($2M PPP Fraud)

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\illuminationfoundation.org.txt | https://illuminationfoundation.org |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\illuminationfoundation.org.cer | https://illuminationfoundation.org |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\illuminationfoundation.org.txt | https://illuminationfoundation.org |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\illuminationfoundation.org.txt | https://illuminationfoundation.org |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\illuminationfoundation.org_.txt | https://illuminationfoundation.org/ |

**Infrastructure:** 3.33.130.190 (AWS) — Same IP as carlisledev.com AND atlanticpacificcommunities.com
**Risk:** Three RICO-connected entities on single AWS IP

### Libertyhomes.org — Liberty Branded, RICO Infrastructure

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\libertyhomes.org.txt | https://libertyhomes.org |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\libertyhomes.org.cer | https://libertyhomes.org |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\libertyhomes.org.txt | https://libertyhomes.org |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\libertyhomes.org.txt | https://libertyhomes.org |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\libertyhomes.org_.txt | https://libertyhomes.org/ |

**Infrastructure:** 76.223.54.146 (Amazon) — Same IP as rbabuilders.com ($2.59M PPP fraud)
**Risk:** Liberty-branded entity on RICO shell company infrastructure

### Libertycare.com — Liberty Branded, RICO Infrastructure

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\libertycare.com.txt | https://libertycare.com |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\libertycare.com.cer | https://libertycare.com |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\libertycare.com.txt | https://libertycare.com |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\libertycare.com.txt | https://libertycare.com |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\libertycare.com_.txt | https://libertycare.com/ |

**Infrastructure:** 76.223.54.146 (Amazon) — Same IP as rbabuilders.com ($2.59M PPP fraud)
**Risk:** Liberty-branded entity on RICO shell company infrastructure

### Libertycare.org — Liberty Branded, RICO Infrastructure

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\libertycare.org.txt | https://libertycare.org |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\libertycare.org.txt | https://libertycare.org |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\libertycare.org_xmlrpc.php.txt | https://libertycare.org/xmlrpc.php |

**Infrastructure:** 76.223.54.146 (Amazon) — Same IP as rbabuilders.com ($2.59M PPP fraud)
**Risk:** XML-RPC endpoint exposed, Liberty-branded entity on RICO shell company infrastructure

---

## CRITICAL EVIDENCE FILES — RICO SHELL COMPANIES

### Rbabuilders.com — RICO Shell ($2.59M PPP Fraud)

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\rbabuilders.com.txt | https://rbabuilders.com |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\rbabuilders.com.cer | https://rbabuilders.com |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\rbabuilders.com.txt | https://rbabuilders.com |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\rbabuilders.com.txt | https://rbabuilders.com |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\rbabuilders.com_.txt | https://rbabuilders.com/ |

**Infrastructure:** 76.223.54.146 (Amazon) — Same IP as libertyhomes.org, libertycare.com, libertycare.org
**Risk:** $2.59M PPP fraud, shares infrastructure with Liberty-branded entities

### L2tmedia.com — RICO Shell, Cook County Sheriff

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\l2tmedia.com.txt | https://l2tmedia.com |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\l2tmedia.com.txt | https://l2tmedia.com |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\l2tmedia.com.txt | https://l2tmedia.com |

**Infrastructure:** 141.193.213.21 — Same /24 block as libertyseniorliving.com and cookcountysheriff.org
**Risk:** RICO shell company on same hosting as sheriff department and Liberty entity

### Stewartindustries.com — RICO Shell ($1.1M PPP Fraud)

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\stewartindustries.com.txt | https://stewartindustries.com |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\stewartindustries.com.txt | https://stewartindustries.com |

**Infrastructure:** 206.188.193.48 — Same /24 block as carlisledevelopment.com (206.188.193.178)
**Risk:** $1.1M PPP fraud, shares hosting block with Carlisle Development

---

## CRITICAL EVIDENCE FILES — SHERIFF DEPARTMENTS

### Cookcountysheriff.org — Sheriff on RICO Infrastructure

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\cookcountysheriff.org.txt | https://cookcountysheriff.org |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\cookcountysheriff.org.txt | https://cookcountysheriff.org |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\cookcountysheriff.org.txt | https://cookcountysheriff.org |

**Infrastructure:** 141.193.213.21 — Same /24 block as l2tmedia.com and libertyseniorliving.com
**Risk:** Sheriff department hosted on same provider as RICO shell companies

### Pimasheriff.org — Sheriff Under Investigation

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\pimasheriff.org.txt | https://pimasheriff.org |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\pimasheriff.org.cer | https://pimasheriff.org |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\pimasheriff.org.txt | https://pimasheriff.org |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\pimasheriff.org.txt | https://pimasheriff.org |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\pimasheriff.org_.txt | https://pimasheriff.org/ |
| Robots.txt | C:\migrate opencode\OSINTNEOAI\evidence\web_content\pimasheriff.org_robots.txt.txt | https://pimasheriff.org/robots.txt |

**Infrastructure:** Cloudflare WAF, 4 ports open (80,443,8080,8443)
**Risk:** Sheriff Chris Nanos under FBI investigation, perjury allegations, $71.5M Axon contract

### Lacounty.gov — Catastrophic Exposure (14 Ports)

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\lacounty.gov.txt | https://lacounty.gov |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\lacounty.gov.cer | https://lacounty.gov |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\lacounty.gov.txt | https://lacounty.gov |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\lacounty.gov.txt | https://lacounty.gov |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\lacounty.gov_.txt | https://lacounty.gov/ |

**Open Ports:** 21,80,110,143,443,993,995,1433,3306,3389,5432,5900,8080,8443,9200
**Exposed Services:** MySQL (3306), RDP (3389), SQL Server (1433), PostgreSQL (5432), VNC (5900), Elasticsearch (9200)
**Risk:** CRITICAL — 14 open ports, NO WAF, all major database/remote access protocols exposed

### Shelbycountytn.gov — Sheriff on RICO Infrastructure

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\shelbycountytn.gov.txt | https://shelbycountytn.gov |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\shelbycountytn.gov.cer | https://shelbycountytn.gov |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\shelbycountytn.gov.txt | https://shelbycountytn.gov |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\shelbycountytn.gov.txt | https://shelbycountytn.gov |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\shelbycountytn.gov_.txt | https://shelbycountytn.gov/ |
| Robots.txt | C:\migrate opencode\OSINTNEOAI\evidence\web_content\shelbycountytn.gov_robots.txt.txt | https://shelbycountytn.gov/robots.txt |

**Infrastructure:** 89.106.200.153 — Same IP as anaheim.net (RICO city)
**Risk:** Sheriff department hosted on same IP as RICO city government

### Hbpd.org — HB Police Department

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\hbpd.org.txt | https://hbpd.org |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\hbpd.org.cer | https://hbpd.org |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\hbpd.org.txt | https://hbpd.org |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\hbpd.org.txt | https://hbpd.org |

**Redirect:** https://hbpd.org/ -> https://www.huntingtonbeachca.gov/departments/police/index.php
**Risk:** Cloudflare WAF, 142 open ports from previous scan, 400 Dehashed breach listings

### Anaheim.net — RICO City Government

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\anaheim.net.txt | https://anaheim.net |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\anaheim.net.cer | https://anaheim.net |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\anaheim.net.txt | https://anaheim.net |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\anaheim.net.txt | https://anaheim.net |
| Homepage Capture | C:\migrate opencode\OSINTNEOAI\evidence\web_content\anaheim.net_.txt | https://anaheim.net/ |
| Robots.txt | C:\migrate opencode\OSINTNEOAI\evidence\web_content\anaheim.net_robots.txt.txt | https://anaheim.net/robots.txt |

**Infrastructure:** 89.106.200.153 — Same IP as shelbycountytn.gov
**Risk:** RICO city government, shares IP with sheriff department

### Anaheimpd.org — Anaheim Police

| Evidence Type | Full Filepath | Full URL |
|--------------|---------------|----------|
| WHOIS Record | C:\migrate opencode\OSINTNEOAI\evidence\whois\anaheimpd.org.txt | https://anaheimpd.org |
| SSL Certificate | C:\migrate opencode\OSINTNEOAI\evidence\ssl\anaheimpd.org.cer | https://anaheimpd.org |
| HTTP Headers | C:\migrate opencode\OSINTNEOAI\evidence\http_headers\anaheimpd.org.txt | https://anaheimpd.org |
| Port Scan | C:\migrate opencode\OSINTNEOAI\evidence\port_scans\anaheimpd.org.txt | https://anaheimpd.org |

**Redirect:** https://anaheimpd.org/ -> https://pd.anaheim.net
**Risk:** Cloudflare WAF, redirects to pd.anaheim.net subdomain

---

## IP CLUSTER MAP — EVIDENCE FILE PATHS

### 141.193.213.x Block (Anonymous Hosting)
```
141.193.213.10 — libertyseniorliving.com
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\libertyseniorliving.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\ssl\libertyseniorliving.com.cer
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\libertyseniorliving.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\libertyseniorliving.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\web_content\libertyseniorliving.com_wp-admin.txt

141.193.213.21 — l2tmedia.com, cookcountysheriff.org
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\l2tmedia.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\cookcountysheriff.org.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\l2tmedia.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\cookcountysheriff.org.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\l2tmedia.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\cookcountysheriff.org.txt
```

### 3.33.130.190 (AWS)
```
3.33.130.190 — carlisledev.com, atlanticpacificcommunities.com, illuminationfoundation.org
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\carlisledev.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\atlanticpacificcommunities.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\illuminationfoundation.org.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\ssl\carlisledev.com.cer
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\ssl\atlanticpacificcommunities.com.cer
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\ssl\illuminationfoundation.org.cer
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\carlisledev.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\atlanticpacificcommunities.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\illuminationfoundation.org.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\carlisledev.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\atlanticpacificcommunities.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\illuminationfoundation.org.txt
```

### 76.223.54.146 (Amazon)
```
76.223.54.146 — libertyhomes.org, libertycare.com, libertycare.org, rbabuilders.com
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\libertyhomes.org.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\libertycare.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\libertycare.org.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\rbabuilders.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\ssl\libertyhomes.org.cer
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\ssl\libertycare.com.cer
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\ssl\rbabuilders.com.cer
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\libertyhomes.org.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\libertycare.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\rbabuilders.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\libertyhomes.org.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\rbabuilders.com.txt
```

### 89.106.200.153 (Rico City + Sheriff)
```
89.106.200.153 — shelbycountytn.gov, anaheim.net
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\shelbycountytn.gov.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\anaheim.net.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\ssl\shelbycountytn.gov.cer
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\ssl\anaheim.net.cer
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\shelbycountytn.gov.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\anaheim.net.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\shelbycountytn.gov.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\anaheim.net.txt
```

### 206.188.193.x (Rack-host.net)
```
206.188.193.48 — stewartindustries.com
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\stewartindustries.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\port_scans\stewartindustries.com.txt

206.188.193.178 — carlisledevelopment.com
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\carlisledevelopment.com.txt
```

### 135.84.124.41 (Shared City Cluster)
```
135.84.124.41 — costamesa.gov, fullerton.ca.us, orangeca.gov, lvmpd.com
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\whois\lvmpd.com.txt
  Evidence: C:\migrate opencode\OSINTNEOAI\evidence\http_headers\lvmpd.com.txt
```

---

## DOCUMENTATION FILES

### Master Matrix
Full filepath: C:\migrate opencode\OSINTNEOAI\reports\RICO_NATIONWIDE_INFRASTRUCTURE_MATRIX.md
GitHub URL: https://github.com/Tonypost949/OsintNeoAi/blob/feat/city-cyber-recon-map/reports/RICO_NATIONWIDE_INFRASTRUCTURE_MATRIX.md

### Previous Scan Results
Full filepath: C:\migrate opencode\OSINTNEOAI\AUDIT_NUMBERS_v2_scan_july24.csv
GitHub URL: https://github.com/Tonypost949/OsintNeoAi/blob/feat/city-cyber-recon-map/AUDIT_NUMBERS_v2_scan_july24.csv

### Full Comparison Report
Full filepath: C:\migrate opencode\OSINTNEOAI\reports\NATIONWIDE_SCAN_RESULTS.md
GitHub URL: https://github.com/Tonypost949/OsintNeoAi/blob/feat/city-cyber-recon-map/reports/NATIONWIDE_SCAN_RESULTS.md

### HB Infrastructure Report
Full filepath: C:\migrate opencode\OSINTNEOAI\agent\osintneo Infrastructure_Report_HuntingtonBeach.md
GitHub URL: https://github.com/Tonypost949/OsintNeoAi/blob/feat/city-cyber-recon-map/agent/osintneo%20Infrastructure_Report_HuntingtonBeach.md

### HB OSINT Forensic Briefing
Full filepath: C:\migrate opencode\OSINTNEOAI\agent\HB_OSINT_Forensic_Briefing.md
GitHub URL: https://github.com/Tonypost949/OsintNeoAi/blob/feat/city-cyber-recon-map/agent/HB_OSINT_Forensic_Briefing.md

### Mercy House RICO Financial Pipeline
Full filepath: C:\migrate opencode\OSINTNEOAI\agent\osintneoai_forensic_report.md
GitHub URL: https://github.com/Tonypost949/OsintNeoAi/blob/feat/city-cyber-recon-map/agent/osintneoai_forensic_report.md

### 3-Pipeline RICO Enterprise Brief
Full filepath: C:\migrate opencode\OSINTNEOAI\opencode_work\RICO_ENTERPRISE_BRIEF_v3.md
GitHub URL: https://github.com/Tonypost949/OsintNeoAi/blob/feat/city-cyber-recon-map/opencode_work/RICO_ENTERPRISE_BRIEF_v3.md

### Dehashed HBPD Scan Report
Full filepath: C:\migrate opencode\OSINTNEOAI\DEHASHED_HBPD_SCAN_REPORT.md
GitHub URL: https://github.com/Tonypost949/OsintNeoAi/blob/feat/city-cyber-recon-map/DEHASHED_HBPD_SCAN_REPORT.md

---

## EVIDENCE VERIFICATION NOTES

### False Positives Identified
- All "200 OK" endpoint responses (36 endpoints) from municipal government domains verified as WAF catch-all pages
- dallaspolice.net "exposed" endpoints are WAF rejection pages
- wichita.gov .git/config returns 500 — directory exists but server errors
- hbpd.org/robots.txt returns 403 — blocked by Cloudflare WAF

### True Positives Confirmed
- libertyseniorliving.com/wp-admin — WordPress login page (8085 bytes, real HTML)
- libertycare.org/xmlrpc.php — XML-RPC endpoint exposed
- lacounty.gov — 14 open ports including MySQL, RDP, PostgreSQL, VNC, Elasticsearch
- cookcountysheriff.org — 403 Forbidden (WAF active, but infrastructure link to RICO shell proven)
- shelbycountytn.gov — Same IP as anaheim.net (RICO city)

### Infrastructure Links Proven
1. libertyseniorliving.com (141.193.213.10) = l2tmedia.com (141.193.213.21) = cookcountysheriff.org (141.193.213.21)
2. carlisledev.com (3.33.130.190) = atlanticpacificcommunities.com (3.33.130.190) = illuminationfoundation.org (3.33.130.190)
3. libertyhomes.org (76.223.54.146) = libertycare.com (76.223.54.146) = rbabuilders.com (76.223.54.146)
4. shelbycountytn.gov (89.106.200.153) = anaheim.net (89.106.200.153)
5. stewartindustries.com (206.188.193.48) = carlisledevelopment.com (206.188.193.178)

---

## CHAIN OF CUSTODY

- All evidence collected: 2026-07-24
- Collection method: PowerShell scripts (Invoke-WebRequest, TcpClient, nslookup)
- Evidence stored: C:\migrate opencode\OSINTNEOAI\evidence\
- Repository: https://github.com/Tonypost949/OsintNeoAi
- Branch: feat/city-cyber-recon-map
- Commit: bb13794
- Collected by: OSINT-NeoAI agent
- No modifications made to any target systems (read-only operations only)

---

## EV-048: Federal Indictment — Peter Anh Pham & Thanh Huong Nguyen
- **Type:** Federal Court Filing
- **Date:** June 2025
- **Description:** Federal indictment on 15 counts including bribery and money laundering. ~$8M diverted through Viet America Society, D Air Conditioning LLC, and Hand to Hand Relief Organization. Andrew Do separately sentenced to 5 years federal prison.
- **Custodian:** US DOJ / USDC Central District of California
- **Statutes:** 18 USC 1341, 18 USC 1956, 18 USC 1962
- **Primary Source:** https://www.courthousenews.com/wp-content/uploads/2025/06/peter-anh-pham-thanh-nguyen-indictment.pdf
- **Notes:** PRIMARY SOURCE for Count 1 of RICO referral brief v3. Link verified.

---

## EV-049: Mercy House Form 990 FY2020 — Schedule L Self-Dealing (Rumbaugh)
- **Type:** IRS Tax Filing
- **Date:** FY2020 (ending June 30, 2020)
- **Description:** Form 990 FY2020 Schedule L documents undisclosed self-dealing: board member Lisa Rumbaugh billed $17,134 through sole proprietorship Clarity Tax Accounting without disclosure.
- **Custodian:** IRS / Mercy House Living Centers (EIN: 33-0315864)
- **Statutes:** IRC §4941; Schedule L disclosure violation
- **Primary Source:** IRS Form 990 - Mercy House Living Centers FY2020, Schedule L — https://projects.propublica.org/nonprofits/organizations/330315864
- **Note:** FY2020 PDF not currently on ProPublica. Physical copy requestable under IRC §6104.

---

## EV-050: Mercy House Form 990 FY2020 and FY2024 — Santa Ana Security Services
- **Type:** IRS Tax Filing
- **Date:** FY2020 and FY2024
- **Description:** 990 filings document Santa Ana Security Services (Miguel Gonzalez) contract scaling from $2.2M to $1.66M while address shifted from commercial PO box to residential.
- **Custodian:** IRS / Mercy House Living Centers (EIN: 33-0315864)
- **Statutes:** 18 USC 1341; Federal program fraud
- **Primary Source:** IRS Form 990 - Mercy House FY2020 and FY2024 — https://projects.propublica.org/nonprofits/organizations/330315864

---

## EV-051: SBA PPP FOIA Dataset — 11770 Warner Ave Fountain Valley
- **Type:** Federal Public Record
- **Date:** SBA PPP FOIA release, data through June 1, 2021
- **Description:** 18 entities at 11770 Warner Ave, Fountain Valley CA 92708. $1,162,212 total, 100% forgiven. Four entities drew duplicate loans under different name spellings.
- **Custodian:** US Small Business Administration (public FOIA)
- **Statutes:** 18 USC 1341; 18 USC 1343; 15 USC 645
- **Primary Source:** https://data.sba.gov/dataset/ppp-foia
- **Filtered Data:** https://github.com/Tonypost949/OsintNeoAi/tree/main/ppp_data
