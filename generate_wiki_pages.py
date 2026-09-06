import json
import os

entities = [
    {
        'id': 'oliver-chi',
        'full_name': 'Oliver Chi',
        'initials': 'OC',
        'official_title': 'City Manager & Real Property Negotiator',
        'agency': 'City of Huntington Beach',
        'risk_score': 9,
        'risk_level': 'CRITICAL (Conflict & Disgorgement Risk)',
        'governing_statutes': ['Cal. Gov. Code § 1090', 'Cal. Gov. Code § 87100', 'Cal. Gov. Code § 54956.8'],
        'surety_bond': 'Cal. Gov. Code § 1480 Official Bond ($500,000 limit)',
        'taxfunded_status': 'AUTO_TRANSFERRED (TX# 0x9a83...4b12)',
        'dossier_summary': 'Designated negotiator on Huntington Beach Navigation Center lease (17631 Cameron / 17642 Beach). Failed to disclose financial interest under § 1090.'
    },
    {
        'id': 'shigeru-yamada',
        'full_name': 'Shigeru Yamada',
        'initials': 'SY',
        'official_title': 'Trustee & Beneficial Landowner',
        'agency': 'Shigeru Yamada Living Trust',
        'risk_score': 9,
        'risk_level': 'CRITICAL (Soil Capping / § 1090 Co-Conspirator)',
        'governing_statutes': ['Cal. Gov. Code § 1090', 'Cal. Health & Safety Code § 25249.6 (Prop 65)'],
        'surety_bond': 'Cal. Civil Code § 9550 Performance Bond',
        'taxfunded_status': 'AUTO_TRANSFERRED (TX# 0x7c12...89ef)',
        'dossier_summary': 'Landowner recipient of municipal lease payments on toxic soil site. Contract included illegal 1-year asphalt cap warranty shortfall.'
    },
    {
        'id': 'mitsuru-yamada',
        'full_name': 'Mitsuru Yamada',
        'initials': 'MY',
        'official_title': 'Trustee & Beneficial Owner',
        'agency': 'Mitsuru Yamada Living Trust',
        'risk_score': 8,
        'risk_level': 'HIGH (Trust Asset Disgorgement Liability)',
        'governing_statutes': ['Cal. Gov. Code § 1090', 'Cal. Gov. Code § 87100'],
        'surety_bond': 'Cal. Civil Code § 9550 Performance Bond',
        'taxfunded_status': 'AUTO_TRANSFERRED (TX# 0x4f91...3a71)',
        'dossier_summary': 'Co-trustee owner of 17642 Beach Blvd parcel involved in non-disclosed municipal shelter leasing.'
    },
    {
        'id': 'robin-estanislau',
        'full_name': 'Robin Estanislau',
        'initials': 'RE',
        'official_title': 'City Clerk & Custodian of Records',
        'agency': 'City of Huntington Beach',
        'risk_score': 7,
        'risk_level': 'HIGH (Records Withholding / CPRA Compliance Failure)',
        'governing_statutes': ['Cal. Gov. Code § 7920 (CPRA)', 'Cal. Gov. Code § 1480'],
        'surety_bond': 'Cal. Gov. Code § 1480 Official Bond',
        'taxfunded_status': 'AUTO_TRANSFERRED (TX# 0x1d22...990c)',
        'dossier_summary': 'Custodian of records subject to statutory CPRA mandates and official bond liability.'
    },
    {
        'id': 'larry-mcneely',
        'full_name': 'Larry McNeely',
        'initials': 'LM',
        'official_title': 'Civic Watchdog & Whistleblower',
        'agency': 'Independent Citizen Audit',
        'risk_score': 1,
        'risk_level': 'VERIFIED_AUDITOR (Protected Shield)',
        'governing_statutes': ['Cal. Gov. Code § 6250 (CPRA)', 'First Amendment Shield', '42 U.S.C. § 1983'],
        'surety_bond': 'N/A (Whistleblower Protection)',
        'taxfunded_status': 'REWARD_ELIGIBLE (OSINT & TFT Tokens)',
        'dossier_summary': 'Exposed public threat, shelter lease bribery concerns, and statutory violations in municipal real estate contracts.'
    }
]

os.makedirs('wiki_pages', exist_ok=True)

for e in entities:
    filename = f"wiki_pages/{e['id']}.html"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Wiki Entry: {e['full_name']} ({e['initials']})</title>
  <style>
    body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 32px; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; max-width: 800px; margin: auto; }}
    h1 {{ color: #58a6ff; margin-top: 0; }}
    .badge {{ padding: 6px 12px; border-radius: 20px; font-weight: bold; background: #7f1d1d; color: #fca5a5; display: inline-block; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th, td {{ border: 1px solid #30363d; padding: 12px; text-align: left; }}
    th {{ background: #21262d; color: #8b949e; width: 30%; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>👤 {e['full_name']} ({e['initials']})</h1>
    <div class="badge">Risk Score: {e['risk_score']}/10 - {e['risk_level']}</div>
    <table>
      <tr><th>Official Title</th><td>{e['official_title']}</td></tr>
      <tr><th>Agency / Entity</th><td>{e['agency']}</td></tr>
      <tr><th>Governing Statutes</th><td>{', '.join(e['governing_statutes'])}</td></tr>
      <tr><th>Surety Bond Status</th><td>{e['surety_bond']}</td></tr>
      <tr><th>TaxFunded Ledger Status</th><td>{e['taxfunded_status']}</td></tr>
      <tr><th>Dossier Summary</th><td>{e['dossier_summary']}</td></tr>
    </table>
    <p><a href="../master_wiki_portal.html" style="color: #58a6ff;">← Back to Master Wiki Sheet Directory</a></p>
  </div>
</body>
</html>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Created standalone Wiki page: {filename}")
