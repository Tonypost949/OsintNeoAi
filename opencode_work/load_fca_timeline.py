import json
import re
from google.cloud import bigquery

client = bigquery.Client(project="noble-beanbag-497411-m4")

# Create schema
schema = [
    bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_date", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("sender", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("recipient", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("subject", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("snippet", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("signal_type", "STRING", mode="REPEATED"),
    bigquery.SchemaField("entity_referenced", "STRING", mode="REPEATED"),
    bigquery.SchemaField("docket_number", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("risk_level", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("tags", "STRING", mode="REPEATED"),
]

table_id = "noble-beanbag-497411-m4.forensic_layers.fca_timeline"
try:
    client.delete_table(table_id)
    print("Deleted existing table")
except:
    pass

table = bigquery.Table(table_id, schema=schema)
client.create_table(table)
print("Created forensic_layers.fca_timeline")

# Email data with forensic tags
events = [
    {
        "event_id": "FCA-HIT-001",
        "event_date": "2026-04-14T16:57:17-07:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "Mr. Knabb (attorney)",
        "subject": "8:26-cv-00348 — Parallel Qui Tam / RICO Evidence Package — Coordination Request",
        "snippet": "Mr. Knabb, My name is Anthony Michael DiMarcello III. I am a federal whistleblower and relator co-prosecuting a False Claims Act qui tam action targeting Mercy House Living Centers and the broader",
        "signal_type": ["FCA_FILING", "RICO_PATTERN", "ATTORNEY_COORDINATION"],
        "entity_referenced": ["Mercy House Living Centers"],
        "docket_number": "8:26-cv-00348",
        "risk_level": "CRITICAL",
        "tags": ["qui_tam", "fca", "federal_docket", "whistleblower", "rico"]
    },
    {
        "event_id": "FCA-HIT-002",
        "event_date": "2026-04-14T16:56:53-07:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "Civil Fraud Unit / False Claims Act Unit (DOJ)",
        "subject": "Supplemental Qui Tam Disclosure — RICO Pattern: OC SSA / Mercy House / SPIN / Angulo NPI / ICWA-IIM Fraud",
        "snippet": "To the Civil Fraud Unit / False Claims Act Unit: This correspondence constitutes a supplemental disclosure to our pending qui tam action against Mercy House Living Centers and related Orange County",
        "signal_type": ["FCA_FILING", "SUPPLEMENTAL_DISCLOSURE", "DOJ_NOTIFICATION"],
        "entity_referenced": ["Mercy House Living Centers", "OC SSA", "SPIN", "Angulo NPI", "ICWA-IIM"],
        "docket_number": None,
        "risk_level": "CRITICAL",
        "tags": ["qui_tam", "fca", "doj", "rico_pattern", "ssa", "icwa"]
    },
    {
        "event_id": "FCA-HIT-003",
        "event_date": "2026-06-11T18:15:04-07:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "ProPublica Nonprofit Accountability Desk",
        "subject": "TIP: Nonprofit accountability — Mercy House charity fraud (unclaimed property + homeless residents poisoning)",
        "snippet": "Mercy House, a California nonprofit claiming to serve homeless populations, is part of a larger conspiracy involving: Environmental poisoning: Placing homeless",
        "signal_type": ["MEDIA_TIP", "ENVIRONMENTAL_POISONING", "UNCLAIMED_PROPERTY"],
        "entity_referenced": ["Mercy House Living Centers", "ProPublica"],
        "docket_number": None,
        "risk_level": "HIGH",
        "tags": ["environmental", "cr_vi", "unclaimed_property", "charity_fraud", "media"]
    },
    {
        "event_id": "FCA-HIT-004",
        "event_date": "2026-05-24T02:23:29-04:00",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "NBC Los Angeles Investigative Unit",
        "subject": "INVESTIGATION TIP: Mercy House Child Deaths + Environmental Poisoning at Homeless Shelter",
        "snippet": "I am submitting a comprehensive OSINT investigation documenting child deaths (4 confirmed), medical emergencies (279), and environmental poisoning (hexavalent chromium)",
        "signal_type": ["MEDIA_TIP", "CHILD_DEATH", "ENVIRONMENTAL_POISONING", "HEXAVALENT_CHROMIUM"],
        "entity_referenced": ["Mercy House Living Centers", "NBC Los Angeles"],
        "docket_number": None,
        "risk_level": "CRITICAL",
        "tags": ["child_death", "cr_vi", "environmental", "medical_emergencies", "navigation_center"]
    },
    {
        "event_id": "FCA-HIT-005",
        "event_date": "2026-05-12T10:52:41-07:00",
        "sender": "Anthony <osintneoai@gmail.com>",
        "recipient": "Unknown",
        "subject": "How would you like to proceed? fuck",
        "snippet": "I have completed the deep-dive search for unclaimed property as requested. The entities Mercy House and Larry Haynes both returned active records within the State Controller's database.",
        "signal_type": ["UNCLAIMED_PROPERTY", "FINANCIAL_ANOMALY"],
        "entity_referenced": ["Mercy House", "Larry Haynes", "CA State Controller"],
        "docket_number": None,
        "risk_level": "HIGH",
        "tags": ["unclaimed_property", "financial", "state_controller"]
    },
    {
        "event_id": "FCA-HIT-006",
        "event_date": "2026-04-22T10:04:52-04:00",
        "sender": "Mercy House <development@mercyhouse.net>",
        "recipient": "Donor List",
        "subject": "Today, your donations will be DOUBLED",
        "snippet": "A video from our CEO Larry Haynes describing Help Them Home and what we do. Thanks to our matching donor, Eastside Christian Church, your donations will be doubled.",
        "signal_type": ["FUNDRAISING", "CHURCH_LINK"],
        "entity_referenced": ["Mercy House", "Eastside Christian Church", "Larry Haynes"],
        "docket_number": None,
        "risk_level": "MEDIUM",
        "tags": ["fundraising", "church_network", "eastside", "matching_donor"]
    },
    {
        "event_id": "FCA-HIT-007",
        "event_date": "2026-04-22T20:30:29-04:00",
        "sender": "Mercy House <development@mercyhouse.net>",
        "recipient": "Donor List",
        "subject": "STATUS UPDATE: We've Hit Our Goal of $50,000! Can we hit our increased goal of $60,000?",
        "snippet": "Thank you for believing in Mercy House and what we do. Can we hit our increased goal of $60,000? We did it! Thank you for believing that everyone deserves a place to call home.",
        "signal_type": ["FUNDRAISING", "GOAL_ESCALATION"],
        "entity_referenced": ["Mercy House"],
        "docket_number": None,
        "risk_level": "LOW",
        "tags": ["fundraising", "donor_list"]
    },
    {
        "event_id": "FCA-HIT-008",
        "event_date": "2025-12-31T12:01:49-05:00",
        "sender": "Mercy House <development@mercyhouse.net>",
        "recipient": "Donor List",
        "subject": "2025: A Year in Review...",
        "snippet": "We couldn't have done it without YOU! DONATE FOLLOW US. Mercy House | PO Box 1905 | Santa Ana, CA 92702",
        "signal_type": ["FUNDRAISING", "ANNUAL_REVIEW"],
        "entity_referenced": ["Mercy House"],
        "docket_number": None,
        "risk_level": "LOW",
        "tags": ["fundraising", "year_end", "annual_report"]
    },
    {
        "event_id": "FCA-HIT-009",
        "event_date": "2025-12-30T12:15:37-05:00",
        "sender": "Mercy House <development@mercyhouse.net>",
        "recipient": "Donor List",
        "subject": "Here's What Your Support Makes Possible",
        "snippet": "In 2025, Mercy House housed or prevented the homelessness of more than 11 people every single day.",
        "signal_type": ["FUNDRAISING", "IMPACT_CLAIM"],
        "entity_referenced": ["Mercy House"],
        "docket_number": None,
        "risk_level": "LOW",
        "tags": ["fundraising", "impact_report"]
    },
    {
        "event_id": "FCA-HIT-010",
        "event_date": "2026-04-08T12:45:29-04:00",
        "sender": "Mercy House <development@mercyhouse.net>",
        "recipient": "Donor List",
        "subject": "We're one family away...",
        "snippet": "Our giving alliance can help 2 families a month, can we make it three? DONATE The Pulse is Mercy House's monthly giving alliance.",
        "signal_type": ["FUNDRAISING", "DONOR_DRIVE"],
        "entity_referenced": ["Mercy House"],
        "docket_number": None,
        "risk_level": "LOW",
        "tags": ["fundraising", "monthly_giving"]
    },
]

# Insert rows
errors = client.insert_rows_json(table_id, events)
if errors:
    print(f"Errors: {errors}")
else:
    print(f"Inserted {len(events)} FCA timeline events")

# Verify
result = client.query(f"SELECT event_id, signal_type, risk_level, docket_number FROM {table_id} ORDER BY event_date DESC").result()
print(f"\n=== FCA TIMELINE ({sum(1 for _ in result)} rows) ===")
client.query(f"SELECT event_id, signal_type, risk_level, docket_number FROM {table_id} ORDER BY event_date DESC").result()

for row in client.query(f"SELECT event_id, risk_level, ARRAY_TO_STRING(signal_type, ', ') AS signals, subject FROM {table_id} WHERE risk_level IN ('CRITICAL', 'HIGH') ORDER BY event_date DESC").result():
    print(f"[{row.risk_level}] {row.event_id} | {row.signals}")
    print(f"  {row.subject[:100]}")
    print()

# Summary counts
for row in client.query(f"SELECT risk_level, COUNT(*) AS cnt FROM {table_id} GROUP BY risk_level ORDER BY cnt DESC").result():
    print(f"  {row.risk_level}: {row.cnt}")
