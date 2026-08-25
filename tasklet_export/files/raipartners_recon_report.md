# 🔍 Target Reconnaissance Report: `raipartners.com`

**Target Domain:** `raipartners.com`  
**Resolved IP:** `198.202.211.1`  
**Date:** August 13, 2026  

---

## 1. Nmap Port Scan Findings
* **Host Status:** Active (0.067s latency)
* **Open Ports:**
  * `80/tcp` (HTTP)
  * `443/tcp` (HTTPS)
  * `8080/tcp` (HTTP-Proxy)
  * `8443/tcp` (HTTPS-alt)

---

## 2. DNS Reconnaissance & Identity Verification
* **DNS SEC:** Enabled
* **Name Servers:** AWS Route 53 (`ns-1015.awsdns-62.net`, `ns-54.awsdns-06.com`, etc.)
* **Mail Servers (MX):** Google Workspace (`aspmx.l.google.com`)
* **TXT Verifications:**
  * **Rippling:** `rippling-domain-verification=8db1f70736d42bc9` (Employee management / HR integration)
  * **Slack:** `slack-domain-verification=w1CyNDlrlvmN1eo1GMteXGEKw7IQIPR5sxSlClzF`
  * **Anthropic:** `anthropic-domain-verification-e52pgv=OwOMKICqdKqGTP0FjhEyLbEdC`
  * **Apple:** `apple-domain-verification=HqsqprFMFuDnkHmS`
  * **Atlassian:** `atlassian-domain-verification=oA1u7XkhNZdiVnyqFttaTTJhOTsgT7gpAUxRxy4SNEXwDf5y6KDrTH2kGWxKTGix`
  * **Webflow:** `proxy-ssl.webflow.com` (Website front-end host)
* **DMARC Policy:** `vDMARC1;p=reject;rua=mailto:8cc31106c0@rua.easydmarc.us` (Managed via EasyDMARC with strict rejection policy)

---

## 3. Initial Web Application Audit
* **Edge Proxy:** Cloudflare detected via banner headers.
* **Missing Security Headers:**
  * Content-Security-Policy (CSP)
  * X-Content-Type-Options
  * Permissions-Policy
  * Strict-Transport-Security (HSTS)
