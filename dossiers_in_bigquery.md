# Forensic Dossiers in BigQuery

The BigQuery dataset `ppp_rico` in project `project-743aab84-f9a5-4ec7-954` contains a table named `forensic_investigative_dossier` containing 13 forensic dossiers and briefs.

Below is the mapping of the table rows (`section_name`), including their associated source filenames, document titles, character lengths, and snippets of their content.

## Table Details
- **Project ID**: `project-743aab84-f9a5-4ec7-954`
- **Dataset ID**: `ppp_rico`
- **Table ID**: `forensic_investigative_dossier`
- **Region**: `us-west1`
- **Total Rows**: `13`

---

## Dossier Index & Mappings

| Section Name | Source File / Metadata | Document Title | Length (chars) | Content Snippet |
| :--- | :--- | :--- | :--- | :--- |
| **`dossier_1`** | [OSINT_Civil_Rights_Integration_Guide.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/OSINT_Civil_Rights_Integration_Guide.md) | OSINT Civil Rights Integration Guide | 3,716 | "This guide establishes the protocols, data pipelines, and..." |
| **`dossier_2`** | [Antigravity_Resurrection_Protocol.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/Antigravity_Resurrection_Protocol.md) | OSINT Neo AI - Diagnostic & Verification Panel Details | 3,784 | "This document compiles the environment v..." |
| **`dossier_3`** | [osintneo Infrastructure_Report_HuntingtonBeach.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/osintneo%20Infrastructure_Report_HuntingtonBeach.md) | OSINT Neo AI Infrastructure Report (HB & SoCal) | 5,506 | "This report detail..." |
| **`dossier_4`** | [osintneoai_forensic_report.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/osintneoai_forensic_report.md) | OSINTNeoAI Forensic Report: Multimodal Enterprise Verification | 8,067 | "## Executive Summary: This re..." |
| **`dossier_5`** | [weaver_audit_analysis.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/weaver_audit_analysis.md) | Forensic Audit and Entity Resolution Analysis Report: Weaver-LMIHAF Network | 19,424 | "## Executive Summar..." |
| **`dossier_6`** | [ENVIRONMENTAL_RICO_PIPELINE.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/ENVIRONMENTAL_RICO_PIPELINE.md) | Environmental RICO Pipeline & CEQA Compliance Forensic Audit | 6,544 | "## Overview: This document deta..." |
| **`dossier_7`** | [CHILD_TRAFFICKING_CPS_LAYER.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/CHILD_TRAFFICKING_CPS_LAYER.md) | Child Trafficking & CPS Layer: Social Care Facility Audit | 4,542 | "## Overview: This document establi..." |
| **`dossier_8`** | [CRIMINAL_REFERRAL_FINAL.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/CRIMINAL_REFERRAL_FINAL.md) | Criminal Referral Exhibit: Institutional Homelessness Fraud & Public Funds Diversion | 7,070 | "## Overvi..." |
| **`dossier_9`** | [HB_OSINT_Forensic_Briefing.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/HB_OSINT_Forensic_Briefing.md) | Huntington Beach Homelessness & Housing Audit Forensic Briefing | 14,110 | "## Executive Summary: This do..." |
| **`dossier_10`** | [CANONICAL_BRIEFING.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/CANONICAL_BRIEFING.md) | Canonical OSINT Briefing: Cross-Jurisdictional Auditing & Entity Resolution | 7,480 | "**Prepared by:**..." |
| **`dossier_11`** | [CANONICAL_BRIEFING_MERCY_HOUSE.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/CANONICAL_BRIEFING_MERCY_HOUSE.md) | Canonical OSINT Briefing: Mercy House & Orange County Homelessness Services Fraud | 14,018 | "**Prepared b...**" |
| **`dossier_12`** | [hbnc_forensic_workbook_phase2.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/hbnc_forensic_workbook_phase2.md) | HBNC Forensic Audit Workbook: Phase 2 Entity Resolution & Remittance Mapping | 9,281 | "**Status:** Conf..." |
| **`dossier_13`** | [resident_pattern_analysis.md](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/agent/resident_pattern_analysis.md) | Resident Pattern & Proximity Analysis Report: Huntington Beach Navigation Center | 47,058 | "**Prepared b...**" |

---

## Verification Query

To query the database directly, run this SQL statement in the BigQuery Console:

```sql
SELECT 
  section_name, 
  JSON_VALUE(parsed_metadata, '$.file_name') AS file_name, 
  LENGTH(content) AS content_length, 
  SUBSTR(content, 1, 150) AS content_preview 
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.forensic_investigative_dossier`
ORDER BY section_name;
```
