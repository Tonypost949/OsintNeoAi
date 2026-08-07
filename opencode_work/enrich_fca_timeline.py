import json
from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

new_events = [
    {
        "event_id": "FCA-HIT-011",
        "event_date": "2026-05-06T17:15:38+00:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "ALL UC HEALTH/COUNSELING SERVICES (UCI, UCLA, USC, UCSD, Berkeley, Stanford)",
        "subject": "MANDATORY REPORT: Dependent Adults Poisoned by Hexavalent Chromium (49x Limit) — Ongoing Federal Case",
        "snippet": "CALIFORNIA WELFARE & INSTITUTIONS CODE § 15630 | MANDATORY REPORTER STATUTE. You are counseling/health services staff at a California postsecondary institution and are a mandated reporter for dependent adult abuse involving environmental poisoning.",
        "signal_type": ["MANDATORY_REPORTER", "ENVIRONMENTAL_POISONING", "HEXAVALENT_CHROMIUM", "INSTITUTIONAL_NOTICE"],
        "entity_referenced": ["UC System", "California Welfare & Institutions Code 15630"],
        "docket_number": None,
        "risk_level": "CRITICAL",
        "tags": ["mandatory_reporter", "uc_system", "health_services", "cr_vi", "49x_limit"]
    },
    {
        "event_id": "FCA-HIT-012",
        "event_date": "2026-05-06T10:15:51-07:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "Orange Coast College President, Saddleback College President, GWC President",
        "subject": "LOCAL ALERT: Huntington Beach Residents Poisoned by Hexavalent Chromium — Mandatory Report Required (Federal Case 8:2026cv00348)",
        "snippet": "URGENT LOCAL ALERT — CALIFORNIA MANDATORY REPORTING STATUTE. You serve the Huntington Beach/Midway City/Orange County community. You are a mandated reporter under California Welfare & Institutions Code.",
        "signal_type": ["MANDATORY_REPORTER", "ENVIRONMENTAL_POISONING", "LOCAL_ALERT", "HEXAVALENT_CHROMIUM"],
        "entity_referenced": ["Orange Coast College", "Saddleback College", "Golden West College", "Huntington Beach"],
        "docket_number": "8:2026cv00348",
        "risk_level": "CRITICAL",
        "tags": ["mandatory_reporter", "community_college", "local_alert", "cr_vi"]
    },
    {
        "event_id": "FCA-HIT-013",
        "event_date": "2026-05-06T10:15:24-07:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "UC Campus Police + Disability Services (UCI, UCLA, UCSD, Berkeley)",
        "subject": "CAMPUS POLICE & DISABILITY SERVICES: Federal Environmental Crime Alert — Hexavalent Chromium Poisoning (49x Limit)",
        "snippet": "FEDERAL ENVIRONMENTAL CRIMES | 42 USC § 6972 (RCRA); 18 USC §§ 241-242. TO CAMPUS POLICE: You have immediate authority and duty to report federal crimes involving environmental poisoning and deprivation of civil rights.",
        "signal_type": ["LAW_ENFORCEMENT", "FEDERAL_CRIME", "RCRA", "CIVIL_RIGHTS", "DISABILITY_RIGHTS"],
        "entity_referenced": ["UC Police", "42 USC 6972", "18 USC 241", "18 USC 242"],
        "docket_number": None,
        "risk_level": "CRITICAL",
        "tags": ["rcra", "civil_rights", "campus_police", "disability", "federal_crime"]
    },
    {
        "event_id": "FCA-HIT-014",
        "event_date": "2026-05-06T10:15:09-07:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "ALL UC NURSING FACULTY (UCI, UCLA, USC, UCSD, Berkeley, Stanford)",
        "subject": "CRITICAL ENVIRONMENTAL HEALTH ALERT: Hexavalent Chromium Poisoning (49x Limit) — Mandatory Report Required",
        "snippet": "CALIFORNIA PENAL CODE § 11165.7(a) | CALIFORNIA NURSING BOARD REPORTING REQUIREMENT. You are a nursing faculty member and mandated reporter. California law requires immediate notification of dependent adult abuse involving environmental poisoning.",
        "signal_type": ["MANDATORY_REPORTER", "ENVIRONMENTAL_POISONING", "HEXAVALENT_CHROMIUM", "NURSING_BOARD"],
        "entity_referenced": ["California Penal Code 11165.7", "CA Nursing Board"],
        "docket_number": None,
        "risk_level": "CRITICAL",
        "tags": ["mandatory_reporter", "nursing", "penal_code", "dependent_adult"]
    },
    {
        "event_id": "FCA-HIT-015",
        "event_date": "2026-05-06T10:14:56-07:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "ALL UC SOCIAL WORK FACULTY (UCI, UCLA, USC, UCSD, UC Davis, Berkeley)",
        "subject": "MANDATORY REPORT REQUIRED: Hexavalent Chromium Poisoning (49x Legal Limit) at OC Shelter — Federal Case 8:2026cv00348",
        "snippet": "CALIFORNIA WELFARE & INSTITUTIONS CODE § 15630 — MANDATORY REPORTER ACTIVATION. You are a mandated reporter at a California postsecondary institution. You have a legal duty to report dependent adult abuse at the Orange County homeless shelter.",
        "signal_type": ["MANDATORY_REPORTER", "ENVIRONMENTAL_POISONING", "HEXAVALENT_CHROMIUM", "SOCIAL_WORK"],
        "entity_referenced": ["California W&I Code 15630", "OC Homeless Shelter"],
        "docket_number": "8:2026cv00348",
        "risk_level": "CRITICAL",
        "tags": ["mandatory_reporter", "social_work", "dependent_adult", "cr_vi"]
    },
    {
        "event_id": "FCA-HIT-016",
        "event_date": "2026-04-14T16:57:17-07:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "LA Times, Voice of OC, CalMatters, OC Register (MEDIA COORDINATION)",
        "subject": "8:26-cv-00348 — Parallel Qui Tam / RICO Evidence Package — Coordination Request",
        "snippet": "Mr. Knabb, My name is Anthony Michael DiMarcello III. I am a federal whistleblower and relator co-prosecuting a False Claims Act qui tam action targeting Mercy House Living Centers.",
        "signal_type": ["FCA_FILING", "MEDIA_COORDINATION", "RICO_PATTERN"],
        "entity_referenced": ["Mercy House Living Centers", "LA Times", "Voice of OC", "CalMatters", "OC Register"],
        "docket_number": "8:26-cv-00348",
        "risk_level": "CRITICAL",
        "tags": ["qui_tam", "fca", "media", "whistleblower", "rico"]
    },
    {
        "event_id": "FCA-HIT-017",
        "event_date": "2026-04-14T16:47:28-07:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "EPA OIG Hotline, EPA Region 9, ICWA-NARF, Disability Rights CA, LAist (FEDERAL + RIGHTS ORGS)",
        "subject": "8:26-cv-00348 — Parallel Qui Tam / RICO Evidence Package — Coordination Request",
        "snippet": "Mr. Knabb, My name is Anthony Michael DiMarcello III. I am a federal whistleblower and relator co-prosecuting a False Claims Act qui tam action targeting Mercy House Living Centers. Notification sent to EPA OIG, ICWA at NARF, Disability Rights California.",
        "signal_type": ["FCA_FILING", "EPA_NOTIFICATION", "ICWA_NOTIFICATION", "DISABILITY_RIGHTS", "TRIBAL_RIGHTS"],
        "entity_referenced": ["EPA OIG", "EPA Region 9", "ICWA", "NARF", "Disability Rights CA", "Mercy House"],
        "docket_number": "8:26-cv-00348",
        "risk_level": "CRITICAL",
        "tags": ["epa", "icwa", "narf", "tribal_rights", "disability_rights", "fca"]
    },
]

table_id = "noble-beanbag-497411-m4.forensic_layers.fca_timeline"
errors = client.insert_rows_json(table_id, new_events)
if errors:
    print(f"Insert errors: {errors}")
else:
    print(f"Inserted {len(new_events)} new FCA timeline events")

# Summary
for row in client.query(f"SELECT risk_level, COUNT(*) AS cnt FROM {table_id} GROUP BY risk_level ORDER BY cnt DESC").result():
    print(f"  {row.risk_level}: {row.cnt}")
print(f"\nTotal timeline events: {sum(1 for _ in client.query(f'SELECT event_id FROM {table_id}').result())}")
