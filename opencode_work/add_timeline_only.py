"""Add CPS timeline events only"""
import os; os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery

client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

print("=" * 70)
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
