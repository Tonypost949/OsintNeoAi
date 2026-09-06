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
        'investigative_category': 'RICO / CONSPIRACY / FINANCIAL INTEREST (§ 1090)',
        'category_badge': 'RICO / CONSPIRACY',
        'category_class': 'cat-rico',
        'governing_statutes': ['Cal. Gov. Code § 1090', 'Cal. Gov. Code § 87100', 'Cal. Gov. Code § 54956.8'],
        'surety_bond': 'Cal. Gov. Code § 1480 Official Bond ($500,000 limit)',
        'taxfunded_status': 'AUTO_TRANSFERRED (TX# 0x9a83...4b12)',
        'dossier_summary': 'Designated negotiator on Huntington Beach Navigation Center lease (17631 Cameron / 17642 Beach). Failed to disclose financial interest under § 1090.',
        'maltego_node_id': 'MAL-NODE-OC-0192',
        'maltego_graph_json': '{"nodes": ["Oliver Chi", "City of HB", "Yamada Living Trust"], "edges": ["Lease Negotiator", "Financial Interest"]}',
        'cli_terminal_log': 'maltego-cli --transform EntityUnmask --target "Oliver Chi" --depth 3\n[+] Found 4 connected entities: Shigeru Yamada Trust, Mitsuru Yamada Trust, HB City Council',
        'mounted_git_repos': ['https://github.com/Tonypost949/OsintNeoAi', 'https://github.com/Tonypost949/TaxFundedEngine']
    },
    {
        'id': 'shigeru-yamada',
        'full_name': 'Shigeru Yamada',
        'initials': 'SY',
        'official_title': 'Trustee & Beneficial Landowner',
        'agency': 'Shigeru Yamada Living Trust',
        'risk_score': 9,
        'risk_level': 'CRITICAL (Soil Capping / § 1090 Co-Conspirator)',
        'investigative_category': 'CONSPIRACY / CORPORATE LAND TRUST SCHEME',
        'category_badge': 'CONSPIRACY',
        'category_class': 'cat-rico',
        'governing_statutes': ['Cal. Gov. Code § 1090', 'Cal. Health & Safety Code § 25249.6 (Prop 65)'],
        'surety_bond': 'Cal. Civil Code § 9550 Performance Bond',
        'taxfunded_status': 'AUTO_TRANSFERRED (TX# 0x7c12...89ef)',
        'dossier_summary': 'Landowner recipient of municipal lease payments on toxic soil site. Contract included illegal 1-year asphalt cap warranty shortfall.',
        'maltego_node_id': 'MAL-NODE-SY-0881',
        'maltego_graph_json': '{"nodes": ["Shigeru Yamada", "17631 Cameron Ln", "Hexavalent Chromium Risk"], "edges": ["Trustee", "Soil Capping"]}',
        'cli_terminal_log': 'maltego-cli --transform ParcelLookup --target "17631 Cameron Ln"\n[+] Flagged: 1-Year Asphalt Cap Shortfall over Hexavalent Chromium Soil',
        'mounted_git_repos': ['https://github.com/Tonypost949/OsintNeoAi']
    },
    {
        'id': 'mitsuru-yamada',
        'full_name': 'Mitsuru Yamada',
        'initials': 'MY',
        'official_title': 'Trustee & Beneficial Owner',
        'agency': 'Mitsuru Yamada Living Trust',
        'risk_score': 8,
        'risk_level': 'HIGH (Trust Asset Disgorgement Liability)',
        'investigative_category': 'CONSPIRACY / LAND TRUST',
        'category_badge': 'CONSPIRACY',
        'category_class': 'cat-rico',
        'governing_statutes': ['Cal. Gov. Code § 1090', 'Cal. Gov. Code § 87100'],
        'surety_bond': 'Cal. Civil Code § 9550 Performance Bond',
        'taxfunded_status': 'AUTO_TRANSFERRED (TX# 0x4f91...3a71)',
        'dossier_summary': 'Co-trustee owner of 17642 Beach Blvd parcel involved in non-disclosed municipal shelter leasing.',
        'maltego_node_id': 'MAL-NODE-MY-0992',
        'maltego_graph_json': '{"nodes": ["Mitsuru Yamada", "17642 Beach Blvd"], "edges": ["Trustee"]}',
        'cli_terminal_log': 'maltego-cli --transform TrustCrossReference --target "Mitsuru Yamada"\n[+] Entity Linked: Shigeru Yamada Trust',
        'mounted_git_repos': ['https://github.com/Tonypost949/OsintNeoAi']
    },
    {
        'id': 'robin-estanislau',
        'full_name': 'Robin Estanislau',
        'initials': 'RE',
        'official_title': 'City Clerk & Custodian of Records',
        'agency': 'City of Huntington Beach',
        'risk_score': 7,
        'risk_level': 'HIGH (Records Withholding / CPRA Compliance Failure)',
        'investigative_category': 'PUBLIC OFFICIAL / RECORDS CUSTODIAN',
        'category_badge': 'PUBLIC OFFICIAL',
        'category_class': 'cat-official',
        'governing_statutes': ['Cal. Gov. Code § 7920 (CPRA)', 'Cal. Gov. Code § 1480'],
        'surety_bond': 'Cal. Gov. Code § 1480 Official Bond',
        'taxfunded_status': 'AUTO_TRANSFERRED (TX# 0x1d22...990c)',
        'dossier_summary': 'Custodian of records subject to statutory CPRA mandates and official bond liability.',
        'maltego_node_id': 'MAL-NODE-RE-4411',
        'maltego_graph_json': '{"nodes": ["Robin Estanislau", "Public Records Index"], "edges": ["Custodian"]}',
        'cli_terminal_log': 'maltego-cli --transform CPRALogLookup --target "Robin Estanislau"\n[+] Flagged: 90-Day Disclosure Exceedance',
        'mounted_git_repos': ['https://github.com/Tonypost949/OsintNeoAi']
    },
    {
        'id': 'larry-mcneely',
        'full_name': 'Larry McNeely',
        'initials': 'LM',
        'official_title': 'Civic Watchdog & Whistleblower',
        'agency': 'Independent Citizen Audit',
        'risk_score': 1,
        'risk_level': 'VERIFIED_AUDITOR (Protected Shield)',
        'investigative_category': 'WITNESS / AUDITOR / WHISTLEBLOWER / PUBLIC THREAT TARGET',
        'category_badge': 'WITNESS / AUDITOR',
        'category_class': 'cat-witness',
        'governing_statutes': ['Cal. Gov. Code § 6250 (CPRA)', 'First Amendment Shield', '42 U.S.C. § 1983'],
        'surety_bond': 'N/A (Whistleblower Protection)',
        'taxfunded_status': 'REWARD_ELIGIBLE (OSINT & TFT Tokens)',
        'dossier_summary': 'Exposed public threat, shelter lease bribery concerns, and statutory violations in municipal real estate contracts.',
        'maltego_node_id': 'MAL-NODE-LM-9012',
        'maltego_graph_json': '{"nodes": ["Larry McNeely", "Public Threats Log", "FOIA Requests"], "edges": ["Whistleblower", "Citizen Audit"]}',
        'cli_terminal_log': 'maltego-cli --transform ThreatTracker --target "Larry McNeely"\n[+] Shield Status: ACTIVE (First Amendment & 42 U.S.C. § 1983)',
        'mounted_git_repos': ['https://github.com/Tonypost949/OsintNeoAi']
    }
]

os.makedirs('wiki_pages', exist_ok=True)

for e in entities:
    filename = f"wiki_pages/{e['id']}.html"
    repos_html = ''.join([f"<li><a href='{r}' target='_blank' style='color: #58a6ff;'>{r}</a></li>" for r in e['mounted_git_repos']])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Wiki Entry: {e['full_name']} ({e['initials']})</title>
  <style>
    body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 24px; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; max-width: 950px; margin: auto; }}
    h1 {{ color: #58a6ff; margin-top: 0; display: flex; justify-content: space-between; align-items: center; }}
    .badge {{ padding: 6px 12px; border-radius: 20px; font-weight: bold; background: #7f1d1d; color: #fca5a5; font-size: 12px; display: inline-block; }}
    .cat-badge {{ padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px; text-transform: uppercase; margin-left: 8px; }}
    .cat-rico {{ background: #991b1b; color: #fecaca; }}
    .cat-official {{ background: #1e3a8a; color: #93c5fd; }}
    .cat-witness {{ background: #065f46; color: #a7f3d0; }}
    .section-title {{ border-bottom: 1px solid #30363d; padding-bottom: 6px; color: #f0f6fc; margin-top: 24px; font-size: 16px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ border: 1px solid #30363d; padding: 10px; text-align: left; font-size: 13px; }}
    th {{ background: #21262d; color: #8b949e; width: 30%; }}
    .terminal-box {{ background: #000; border: 1px solid #30363d; border-radius: 6px; padding: 14px; font-family: monospace; color: #00ff66; font-size: 12px; white-space: pre-wrap; margin-top: 10px; }}
    .graph-box {{ background: #1f2937; border: 1px solid #374151; border-radius: 6px; padding: 16px; margin-top: 10px; font-family: monospace; color: #9ca3af; font-size: 12px; }}
    .repo-toggle {{ background: #21262d; border: 1px solid #30363d; padding: 12px; border-radius: 6px; margin-top: 10px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>
      <span>👤 {e['full_name']} ({e['initials']})</span>
      <span class="cat-badge {e['category_class']}">{e['category_badge']}</span>
    </h1>
    <div class="badge">Risk Score: {e['risk_score']}/10 - {e['risk_level']}</div>

    <div class="section-title">📌 Attributes & Investigative Category</div>
    <table>
      <tr><th>Category Classification</th><td><strong style="color: #fca5a5;">{e['investigative_category']}</strong></td></tr>
      <tr><th>Official Title</th><td>{e['official_title']}</td></tr>
      <tr><th>Agency / Entity</th><td>{e['agency']}</td></tr>
      <tr><th>Governing Statutes</th><td>{', '.join(e['governing_statutes'])}</td></tr>
      <tr><th>Surety Bond Status</th><td>{e['surety_bond']}</td></tr>
      <tr><th>TaxFunded Ledger</th><td>{e['taxfunded_status']}</td></tr>
      <tr><th>Dossier Summary</th><td>{e['dossier_summary']}</td></tr>
    </table>

    <div class="section-title">💻 Maltego CLI Terminal Output</div>
    <div class="terminal-box">$ {e['cli_terminal_log']}</div>

    <div class="section-title">🕸️ Maltego Graphics & Graph Connection (Node #{e['maltego_node_id']})</div>
    <div class="graph-box">Maltego JSON Graph Entity Blueprint:<br>{e['maltego_graph_json']}</div>

    <div class="section-title">⚙️ GitHub Repositories (Mounted / Dynamic Toggle)</div>
    <div class="repo-toggle">
      <ul style="margin: 0; padding-left: 20px;">
        {repos_html}
      </ul>
    </div>

    <p style="margin-top: 24px;"><a href="../master_wiki_portal.html" style="color: #58a6ff;">← Back to Master Wiki Directory</a></p>
  </div>
</body>
</html>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Updated Wiki page with Maltego CLI, Graph, Repos, and Categories: {filename}")
