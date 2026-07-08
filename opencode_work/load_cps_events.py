from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

events = [
    {
        'event_id': 'CPS-001',
        'event_date': '2026-06-10T15:14:42-07:00',
        'sender': 'Anthony DiMarcello <amd949609@gmail.com>',
        'recipient': 'FBI Investigators',
        'subject': 'MANDATORY REPORTER ACTIVATION: CERCLA Chemical Emergency + Child Trafficking + 5 Years Blocked Reporting',
        'snippet': 'Emergency federal whistleblower report and mandatory reporter activation. OC Child Welfare Trafficking Network. CERCLA chemical emergency at HBNC. 5 years of blocked reporting.',
        'signal_type': ['FBI_NOTIFICATION', 'CHILD_TRAFFICKING', 'CERCLA', 'MANDATORY_REPORTER', 'BLOCKED_REPORTING'],
        'entity_referenced': ['FBI', 'OC Child Welfare', 'CERCLA', 'HBNC'],
        'docket_number': None,
        'risk_level': 'CRITICAL',
        'tags': ['cps', 'child_trafficking', 'fbi', 'cercla', 'mandatory_reporter']
    },
    {
        'event_id': 'CPS-002',
        'event_date': '2026-04-15T14:45:58-07:00',
        'sender': 'Anthony DiMarcello <amd949609@gmail.com>',
        'recipient': 'USC and UCLA Schools of Social Work',
        'subject': 'URGENT: Whistleblower Evidence - $340M+ Federal Fraud Network - OC Child Welfare Trafficking',
        'snippet': 'Evidence of systematic child welfare trafficking and fraud affecting Orange County. CPS removals used as billing mechanism through federal IV-E reimbursement.',
        'signal_type': ['CHILD_TRAFFICKING', 'INSTITUTIONAL_NOTICE', 'IV_E_FRAUD', 'CPS_FRAUD'],
        'entity_referenced': ['USC School of Social Work', 'UCLA School of Social Welfare', 'OC SSA', 'Title IV-E'],
        'docket_number': None,
        'risk_level': 'CRITICAL',
        'tags': ['cps', 'child_trafficking', '340M', 'iv_e', 'social_work']
    },
    {
        'event_id': 'CPS-003',
        'event_date': '2026-05-24T00:00:00-07:00',
        'sender': 'Anthony DiMarcello <amd949609@gmail.com>',
        'recipient': 'KABC-TV, Voice of OC, ProPublica',
        'subject': '$512M+ COVID/CARES Fraud involving Child Welfare Trafficking Network',
        'snippet': 'Systematic child welfare trafficking through Mercy House Living Centers. $512M+ in COVID/CARES fraud. 4 confirmed child deaths, 279 medical emergencies at HBNC.',
        'signal_type': ['CHILD_TRAFFICKING', 'MEDIA_TIP', 'COVID_FRAUD', 'CHILD_DEATH'],
        'entity_referenced': ['Mercy House', 'HBNC', 'CARES Act', 'KABC-TV', 'Voice of OC'],
        'docket_number': None,
        'risk_level': 'CRITICAL',
        'tags': ['cps', '512M', 'child_death', 'cares_act', 'mercy_house']
    },
    {
        'event_id': 'CPS-004',
        'event_date': '2026-05-27T00:00:00-07:00',
        'sender': 'Anthony DiMarcello <amd949609@gmail.com>',
        'recipient': 'HUD OIG / DOJ Civil Fraud Unit',
        'subject': 'FINAL NOTICE: HUD FCA / 31 USC 3730 Automatic Qui Tam Trigger',
        'snippet': 'FINAL NOTICE triggering 31 USC 3730 automatic qui tam provisions. HUD False Claims Act violation involving child welfare trafficking through HUD-funded shelters.',
        'signal_type': ['FCA_TRIGGER', 'HUD_FCA', 'CHILD_TRAFFICKING', 'SHELTER_FRAUD'],
        'entity_referenced': ['HUD OIG', 'DOJ Civil Fraud Unit', 'Mercy House', '31 USC 3730'],
        'docket_number': None,
        'risk_level': 'CRITICAL',
        'tags': ['cps', 'hud_fca', 'qui_tam', '31_usc_3730', 'shelter_fraud']
    },
    {
        'event_id': 'CPS-005',
        'event_date': '2024-01-01T00:00:00-08:00',
        'sender': 'OC SSA (Systemic)',
        'recipient': 'HHS/ACF Title IV-E Program',
        'subject': '30,000 CPS removals/year in Orange County - $200M-$300M/yr IV-E reimbursement pipeline',
        'snippet': 'OC SSA makes 30,000 CPS dispatches per year. Each removal triggers federal Title IV-E per-diem reimbursement. Gap between removals (30K) and homeless PIT (700) is 97.7% - 29,300 children unaccounted.',
        'signal_type': ['CPS_REMOVAL', 'IV_E_BILLING', 'GHOST_BILLING', 'SYSTEMIC_FRAUD'],
        'entity_referenced': ['OC SSA', 'HHS', 'ACF', 'Title IV-E', '42 USC 671-679b'],
        'docket_number': None,
        'risk_level': 'CRITICAL',
        'tags': ['cps', 'iv_e', 'ghost_billing', '200M', 'removal_pipeline']
    },
]

table_id = 'noble-beanbag-497411-m4.forensic_layers.fca_timeline'
errors = client.insert_rows_json(table_id, events)
if errors:
    print(f'Errors: {errors}')
else:
    print(f'Inserted {len(events)} CPS pipeline events into fca_timeline')

for row in client.query(f'SELECT risk_level, COUNT(*) as cnt FROM {table_id} GROUP BY risk_level ORDER BY cnt DESC').result():
    print(f'  {row.risk_level}: {row.cnt}')

total = list(client.query(f'SELECT COUNT(*) as c FROM {table_id}').result())[0].c
print(f'Total FCA timeline events: {total}')
