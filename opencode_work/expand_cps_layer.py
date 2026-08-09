"""Add CPS/child trafficking layer nodes and timeline events"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
from datetime import datetime

client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=" * 70)
print("ADDING CPS/CHILD TRAFFICKING LAYER NODES")
print("=" * 70)

new_nodes = [
    {
        "node_id": "ORG_211",
        "node_type": "NONPROFIT",
        "node_name": "211 OC / Orange County United Way",
        "layer": "CPS_PIPELINE",
        "connected_to": ["OCSSA", "MERCY-001", "ENV-001"],
        "connection_type": "HMIS_REFERRAL",
        "evidence_ref": "HMIS database controller; referral pipeline to Mercy House/HBNC",
        "risk_level": "HIGH",
        "notes": "Controls HMIS database; routes CPS referrals to shelter system including toxic HBNC site"
    },
    {
        "node_id": "FUND_IV_E",
        "node_type": "FEDERAL_PROGRAM",
        "node_name": "Title IV-E Federal Foster Care Program",
        "layer": "CPS_PIPELINE",
        "connected_to": ["OCSSA", "MERCY-001"],
        "connection_type": "FUNDING",
        "evidence_ref": "42 USC 671-679b; per-child per-diem reimbursement",
        "risk_level": "CRITICAL",
        "notes": "OC draws $200M-$300M+/year in IV-E reimbursements at 30K removals/year; potential ghost billing"
    },
    {
        "node_id": "CASE_ICWA",
        "node_type": "FRAUD_PATTERN",
        "node_name": "ICWA-IIM Systematic Fraud Pattern",
        "layer": "CPS_PIPELINE",
        "connected_to": ["OCSSA", "ICWA-001"],
        "connection_type": "FRAUD_SCHEME",
        "evidence_ref": "25 USC 1901-1963; 18 USC 1163; DOI/BIA OIG complaints filed",
        "risk_level": "CRITICAL",
        "notes": "Improper Native child removal + IIM trust fund theft; $200M+ diverted; DOI OIG complaints 2026-04-14, 2026-04-19, 2026-05-08"
    },
    {
        "node_id": "EVID_CHILD_DEATHS",
        "node_type": "EVIDENCE",
        "node_name": "4 Child Deaths + 279 Medical Emergencies",
        "layer": "CPS_PIPELINE",
        "connected_to": ["MERCY-001", "ENV-001"],
        "connection_type": "EVIDENCE_OF",
        "evidence_ref": "Qui tam filings; MSG:19e58a72739d3470",
        "risk_level": "CRITICAL",
        "notes": "Hexavalent chromium poisoning at 49x EPA limit; documented in qui tam disclosures May 2026"
    },
    {
        "node_id": "EVID_TRAFFICKING",
        "node_type": "EVIDENCE",
        "node_name": "$512M+ COVID Child Welfare Fraud",
        "layer": "CPS_PIPELINE",
        "connected_to": ["MERCY-001", "OCSSA"],
        "connection_type": "EVIDENCE_OF",
        "evidence_ref": "MSG:19e58a7319030f45; KABC-TV tip; Voice of OC investigation",
        "risk_level": "CRITICAL",
        "notes": "CARES Act fraud involving child welfare trafficking network; tips to KABC-TV and LAist May 2026"
    }
]

insert_count = 0
for node in new_nodes:
    check_q = f"""
    SELECT COUNT(*) as cnt FROM `{PRJ}.forensic_layers.rico_network_map`
    WHERE node_id = '{node["node_id"]}'
    """
    existing = list(client.query(check_q).result())[0]['cnt']
    
    if existing == 0:
        connected_str = "', '".join(node["connected_to"])
        insert_q = f"""
        INSERT INTO `{PRJ}.forensic_layers.rico_network_map`
        (node_id, node_type, node_name, layer, connected_to, connection_type, 
         evidence_ref, risk_level, notes)
        VALUES (
            '{node["node_id"]}',
            '{node["node_type"]}',
            '{node["node_name"]}',
            '{node["layer"]}',
            ['{connected_str}'],
            ['{node["connection_type"]}'],
            '{node["evidence_ref"]}',
            '{node["risk_level"]}',
            '{node["notes"]}'
        )
        """
        client.query(insert_q).result()
        print(f"  + Added: {node['node_id']} - {node['node_name'][:50]}")
        insert_count += 1
    else:
        print(f"  = Exists: {node['node_id']}")

print(f"\nNew nodes added: {insert_count}")

print("\n" + "=" * 70)
print("UPDATING EXISTING NODE CONNECTIONS")
print("=" * 70)

updates = [
    {
        "node_id": "MERCY-001",
        "add_connections": ["ORG_211", "FUND_IV_E", "EVID_CHILD_DEATHS", "EVID_TRAFFICKING"],
        "notes_add": "CPS pipeline: receives IV-E funded placements; 4 child deaths; $512M+ COVID fraud"
    },
    {
        "node_id": "ENV-001",
        "add_connections": ["EVID_CHILD_DEATHS", "ORG_211"],
        "notes_add": "CPS placement site; hexavalent Cr caused child deaths"
    },
    {
        "node_id": "OCSSA",
        "add_connections": ["FUND_IV_E", "CASE_ICWA", "ORG_211"],
        "notes_add": "IV-E billing authority; ICWA-IIM fraud pattern; routes through 211 OC"
    }
]

for upd in updates:
    connections_str = "', '".join(upd["add_connections"])
    update_q = f"""
    UPDATE `{PRJ}.forensic_layers.rico_network_map`
    SET connected_to = ARRAY_CONCAT(COALESCE(connected_to, []), ['{connections_str}']),
        notes = CONCAT(COALESCE(notes, ''), ' | {upd["notes_add"]}')
    WHERE node_id = '{upd["node_id"]}'
    """
    client.query(update_q).result()
    print(f"  ~ Updated: {upd['node_id']}")

print("\n" + "=" * 70)
print("LOADING NEW EMAIL EVIDENCE TO TIMELINE")
print("=" * 70)

email_evidence = [
    {
        "event_id": "CPS-006",
        "event_date": "2026-05-27 20:13:52",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "University Leadership (Social Work, Nursing)",
        "subject": "MANDATORY REPORTER ALERT: v11 Orange County Child Welfare + Homeless Services Fraud",
        "snippet": "OC Fraud Network + Child Welfare Pipeline; mandatory reporter activation to universities",
        "signal_type": "WHISTLEBLOWER_TIP",
        "entity_referenced": ["OC SSA", "Mercy House", "Universities"],
        "risk_level": "HIGH",
        "tags": ["mandatory-reporter", "child-welfare", "universities"]
    },
    {
        "event_id": "CPS-007",
        "event_date": "2026-05-24 02:23:32",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "KABC-TV (ABC 7) News Tips",
        "subject": "INVESTIGATION TIP: Orange County COVID Fraud + Child Welfare Trafficking Network",
        "snippet": "$512M+ COVID/CARES fraud involving child welfare trafficking network",
        "signal_type": "MEDIA_TIP",
        "entity_referenced": ["Mercy House", "OC SSA", "KABC-TV"],
        "risk_level": "CRITICAL",
        "tags": ["media", "covid-fraud", "trafficking"]
    },
    {
        "event_id": "CPS-008",
        "event_date": "2026-05-24 02:23:21",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "LAist Investigative Team",
        "subject": "INVESTIGATION TIP: Orange County Child Welfare Trafficking - Mercy House Living Centers",
        "snippet": "Systematic child welfare trafficking through Mercy House Living Centers",
        "signal_type": "MEDIA_TIP",
        "entity_referenced": ["Mercy House", "LAist"],
        "risk_level": "CRITICAL",
        "tags": ["media", "trafficking", "mercy-house"]
    },
    {
        "event_id": "CPS-009",
        "event_date": "2026-05-24 02:21:55",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "California DSS Fraud Unit",
        "subject": "California DSS Fraud Unit: ICWA/IIM Systematic Fraud - OC Fraud Network v10",
        "snippet": "Systematic fraud within OC Social Services involving Indian Child Welfare Act violations",
        "signal_type": "REGULATORY_COMPLAINT",
        "entity_referenced": ["OC SSA", "CA DSS", "ICWA"],
        "risk_level": "CRITICAL",
        "tags": ["dss", "icwa", "iim", "regulatory"]
    },
    {
        "event_id": "CPS-010",
        "event_date": "2026-04-14 16:57:45",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "Bureau of Trust Funds Administration, DOI",
        "subject": "IIM Account Misappropriation Tip - Orange County SSA / Foster Care Trustee Petition",
        "snippet": "Federal whistleblower tip regarding IIM trust fund misappropriation",
        "signal_type": "FEDERAL_TIP",
        "entity_referenced": ["OC SSA", "DOI", "Bureau of Trust Funds"],
        "risk_level": "CRITICAL",
        "tags": ["iim", "doi", "trust-funds"]
    },
    {
        "event_id": "CPS-011",
        "event_date": "2026-04-14 16:57:32",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "LAist Investigative Desk",
        "subject": "Investigative Tip - OC Toxic Shelter / Medicaid Fraud / Native Child IIM Theft",
        "snippet": "Interconnected fraud network: toxic shelter, Medicaid fraud, Native child IIM theft",
        "signal_type": "MEDIA_TIP",
        "entity_referenced": ["Mercy House", "HBNC", "LAist"],
        "risk_level": "CRITICAL",
        "tags": ["media", "toxic-shelter", "medicaid", "iim"]
    },
    {
        "event_id": "CPS-012",
        "event_date": "2026-04-14 16:56:53",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "DOJ Civil Fraud Unit",
        "subject": "Supplemental Qui Tam Disclosure - RICO Pattern: OC SSA / Mercy House / SPIN / Angulo NPI / ICWA-IIM Fraud",
        "snippet": "Supplemental disclosure to pending qui tam action; RICO pattern documented",
        "signal_type": "QUI_TAM",
        "entity_referenced": ["OC SSA", "Mercy House", "SPIN", "Marcus Angulo", "DOJ"],
        "risk_level": "CRITICAL",
        "tags": ["qui-tam", "rico", "supplemental"]
    },
    {
        "event_id": "CPS-013",
        "event_date": "2026-04-14 16:52:19",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "FBI FOIPA",
        "subject": "IIM Account Misappropriation Tip - Orange County SSA / Foster Care Trustee Petition",
        "snippet": "Forwarded IIM misappropriation tip to FBI",
        "signal_type": "FEDERAL_TIP",
        "entity_referenced": ["FBI", "OC SSA", "IIM"],
        "risk_level": "HIGH",
        "tags": ["fbi", "iim", "forwarded"]
    },
    {
        "event_id": "CPS-014",
        "event_date": "2026-04-14 16:47:10",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "EPA OIG Hotline",
        "subject": "Investigative Tip - OC Toxic Shelter / Medicaid Fraud / Native Child IIM Theft",
        "snippet": "EPA OIG received tip regarding toxic shelter and interconnected fraud",
        "signal_type": "FEDERAL_TIP",
        "entity_referenced": ["EPA OIG", "Mercy House", "HBNC"],
        "risk_level": "CRITICAL",
        "tags": ["epa", "toxic", "iim"]
    },
    {
        "event_id": "CPS-015",
        "event_date": "2026-04-19 02:18:09",
        "sender": "Anthony DiMarcello <amd949609@gmail.com>",
        "recipient": "DOI Office of Inspector General",
        "subject": "ICWA/IIM Fraud Complaint - OC SSA Systematic Non-Inquiry + $200M Trust Fund Abuse",
        "snippet": "Indian Child Welfare Act / Indian Individual Money fraud complaint",
        "signal_type": "FEDERAL_COMPLAINT",
        "entity_referenced": ["DOI OIG", "OC SSA", "ICWA", "IIM"],
        "risk_level": "CRITICAL",
        "tags": ["doi-oig", "icwa", "iim", "200m"]
    }
]

timeline_count = 0
for event in email_evidence:
    check_q = f"""
    SELECT COUNT(*) as cnt FROM `{PRJ}.forensic_layers.fca_timeline`
    WHERE event_id = '{event["event_id"]}'
    """
    existing = list(client.query(check_q).result())[0]['cnt']
    
    if existing == 0:
        entities_str = "', '".join(event["entity_referenced"])
        tags_str = "', '".join(event["tags"])
        
        insert_q = f"""
        INSERT INTO `{PRJ}.forensic_layers.fca_timeline`
        (event_id, event_date, sender, recipient, subject, snippet, signal_type, 
         entity_referenced, risk_level, tags)
        VALUES (
            '{event["event_id"]}',
            TIMESTAMP('{event["event_date"]}'),
            '{event["sender"]}',
            '{event["recipient"]}',
            '{event["subject"]}',
            '{event["snippet"]}',
            ['{event["signal_type"]}'],
            ['{entities_str}'],
            '{event["risk_level"]}',
            ['{tags_str}']
        )
        """
        client.query(insert_q).result()
        print(f"  + Added: {event['event_id']} - {event['subject'][:60]}")
        timeline_count += 1
    else:
        print(f"  = Exists: {event['event_id']}")

print(f"\nNew timeline events added: {timeline_count}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"New network nodes added: {insert_count}")
print(f"Existing nodes updated: {len(updates)}")
print(f"New timeline events added: {timeline_count}")
print(f"Total CPS-related emails found: 39")
print("=" * 70)
