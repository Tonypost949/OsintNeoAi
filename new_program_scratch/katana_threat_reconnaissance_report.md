# KATANA CRAWL THREAT RECONNAISSANCE REPORT
## EXECUTIVE SYSTEM AUDIT

- **Total Scan Footprint:** 402253 URLs
- **Unique Authority Domains Scanned:** 4645
- **Flagged Exposed Admin/Config Nodes:** 16585 URLs

## TOP EXPOSED MUNICIPALITY & AGENCY DOMAINS

| Domain | Total Scanned URLs | Flagged Admin Paths | Security Status |
| :--- | :---: | :---: | :--- |
| newportbeachca.gov | 96587 | 8729 | **EXPOSED** |
| www.michigan.gov | 23744 | 108 | **EXPOSED** |
| transparencia.pr.gov | 22377 | 0 | **CLEAN** |
| www.oregon.gov | 19797 | 59 | **EXPOSED** |
| www.nbpd.org | 14098 | 1752 | **EXPOSED** |
| www.edison.com | 12502 | 0 | **CLEAN** |
| www.newportbeachca.gov | 11668 | 754 | **EXPOSED** |
| turkiye.gov.tr | 9365 | 0 | **CLEAN** |
| www.nd.gov | 8687 | 0 | **CLEAN** |
| ggchamber.com | 8639 | 161 | **EXPOSED** |
| wa.gov | 8335 | 2 | **CLEAN** |
| www.huntingtonbeachcu.org | 8188 | 0 | **CLEAN** |
| www.nbchamber.com | 7028 | 0 | **CLEAN** |
| www.iowa.gov | 4737 | 10 | **FLAG** |
| www.googletagmanager.com | 4273 | 0 | **CLEAN** |
| istanbul.pol.tr | 3964 | 0 | **CLEAN** |
| www.facebook.com | 3668 | 0 | **CLEAN** |
| portal.ct.gov | 3630 | 8 | **FLAG** |
| www.ri.gov | 3080 | 4 | **FLAG** |
| www.illinois.gov | 2783 | 105 | **EXPOSED** |
| www.wisconsin.gov | 2733 | 8 | **FLAG** |
| www.courts.oregon.gov | 2606 | 0 | **CLEAN** |
| twitter.com | 2569 | 0 | **CLEAN** |
| fonts.googleapis.com | 2532 | 0 | **CLEAN** |
| energized.edison.com | 2327 | 0 | **CLEAN** |
| www.youtube.com | 2258 | 0 | **CLEAN** |
| portal.ehawaii.gov | 2048 | 0 | **CLEAN** |
| www.linkedin.com | 1879 | 0 | **CLEAN** |
| newsroom.edison.com | 1786 | 0 | **CLEAN** |
| sos.oregon.gov | 1654 | 0 | **CLEAN** |

## DETAILED ACTIONABLE MITIGATION STEPS
1. **Path Hardening:** Restrict access to all `/admin`, `_config`, and backend `.jsp` services behind zero-trust networks.
2. **Revize CMS & Legistar Access Control:** Coordinate with municipal web managers to implement IP-whitelisting on content publishing modules.
