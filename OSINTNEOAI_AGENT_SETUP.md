# OsintNeoAi Agent Setup & Transfer Guide

**Version:** August 2026
**Owner:** Anthony DiMarcello III
**Repo:** https://github.com/Tonypost949/OsintNeoAi
**Case:** CACD Case 8:2026cv00348

---

## Quick Start

### Day 1
1. Auth connections: Gmail, Drive, Tasks, Calendar, GitHub
2. `git clone https://github.com/Tonypost949/OsintNeoAi.git`
3. `pip install maxminddb geoip2 requests google-cloud-bigquery`
4. Load AGENTS.md into agent memory

### Day 2
1. Gmail trigger: incoming mail → OCR → classify → case file
2. 20-min OCR schedule trigger
3. Distribution wave automation

### Day 3
1. Test: `python agent/city_ip_geolocation.py --ips 8.8.8.8`
2. Verify Gmail trigger, Tasks sync, GitHub push

---

## Connections

| Service | Account | Purpose |
|---|---|---|
| Gmail | amd949609@gmail.com | Evidence intake, distributions |
| Google Drive | same | File backup |
| Google Tasks | same | Action queue |
| Google Calendar | same | Deadlines |
| GitHub | Tonypost949 | Evidence repo |

---

## Geolocation Scripts

```bash
# Single IP
python agent/city_ip_geolocation.py --ips 8.8.8.8

# Bulk from file
python agent/city_ip_geolocation.py --file ips.txt

# By city
python agent/city_ip_geolocation.py --city "Huntington Beach"

# All CA cities
python agent/bulk_city_ip_scanner.py --scan-california-cities
```

---

## Active Case Files (in Tasklet /tasklet/agent/home/)

### Master Reports
- OC_Fraud_Network_OSINT_Report_v16.1_HBNC_ENVIRONMENTAL_FRAUD_MANDATORY_REPORTER.md (33K)
- OC_Fraud_Network_OSINT_Report_v16_INTEGRATED.md (28K)
- OC_Fraud_Network_OSINT_Report.md (153K archive)

### HBNC
- LEGISTAR_FILE_25_467_MERCY_HOUSE_CONTRACT_VERIFIED.md
- HBNC_ENVIRONMENTAL_FRAUD_SYNTHESIS_JUNE2026.md
- FEDERAL_EMERGENCY_MOTION_HBNC_CLOSURE_YAMADA_CONSPIRACY.md
- DOJ_MOTION_HBNC_EMERGENCY_CLOSURE.md

### Unclaimed Property
- ALL_STATES_UNCLAIMED_PROPERTY_FINAL_REPORT.md
- UNCLAIMED_PROPERTY_DATABASE_SCREENSHOTS_VERIFIED_SESSION_7_26.md
- UNCLAIMED_PROPERTY_ASSET_SEIZURE_BRIEF.md
- CIVIL_FORFEITURE_PHAM_WELLS_FARGO.md

### Chen / Yamada / SoCal Edison
- CHEN_YAMADA_SOCAL_EDISON_INVESTIGATION_FULL.md
- SOCAL_EDISON_CHEN_YAMADA_TRANSMISSION_INVESTIGATION.md
- WRA_YAMADA_FINDINGS_BREAKDOWN_JUNE2026.md

### Knabb Case
- JESSE_KNABB_CASE_DOCKETS_COMPLETE.md
- KNABB_CRIMINAL_REFERRAL_ANALYSIS_v1.md
- CRIMINAL_REFERRAL_FRAMEWORK_KNABB_CASE.md

### Legal & Motions
- MOTION_TO_VACATE_BRIEF_v2.md
- FEDERAL_DEFAULTS_AND_STATUTORY_OBLIGATIONS.md
- IRS_FORM_211_MERCY_HOUSE_DRAFT.md
- ESCALATION_EMAIL_FINCEN_DRAFT.md

### Distribution
- WAVE_7_FINAL_COMPREHENSIVE_v15.md
- DISTRIBUTION_EMAIL_DRAFT_v15.md
- OUTREACH_DISTRIBUTION_STRATEGY_v16.md

### NPI & Records
- NPI_DELETION_EVIDENCE_COMPARATIVE_ANALYSIS_JUNE_4_2026.md
- COMPREHENSIVE_RECORD_DELETION_LAW_AND_PRECEDENT_JUNE_4_2026.md
- DR_ANN_VERMA_FEDERAL_RECORDS_DELETION_FORENSIC_REPORT.md

### Shea Homes
- SHEA_CAMERON_LANE_ENVIRONMENTAL_FINDINGS_SYNTHESIS.md
- SHEA_HOMES_TRIBAL_CONSULTATION_FAILURE_BRIEF.md

### Whistleblower
- WHISTLEBLOWER_RECOVERY_CALCULATION.md
- REVISED_WHISTLEBLOWER_RECOVERY.md

---

*OsintNeoAi | August 2026*