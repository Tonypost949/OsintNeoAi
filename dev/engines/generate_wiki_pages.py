import json
import os

page_types_database = [
    # 1. PAGE TYPE: PERSON (Government Official / Trustee / Whistleblower)
    {
        'id': 'oliver-chi',
        'page_type': 'PERSON',
        'type_icon': '👤',
        'full_name': 'Oliver Chi',
        'initials': 'OC',
        'official_title': 'City Manager & Real Property Negotiator',
        'agency': 'City of Huntington Beach',
        'risk_score': 9,
        'risk_level': 'CRITICAL (Conflict & Disgorgement Risk)',
        'category_badge': 'PUBLIC OFFICIAL / RICO',
        'category_class': 'cat-rico',
        'governing_statutes': ['Cal. Gov. Code § 1090', 'Cal. Gov. Code § 87100', 'Cal. Gov. Code § 54956.8'],
        'surety_bond': 'Cal. Gov. Code § 1480 Official Bond ($500,000 limit)',
        'whistleblower_payout_rule': 'Eligible under Cal. Gov. Code § 12650 False Claims Act (15% - 33% Share)',
        'dossier_summary': 'Designated negotiator on Huntington Beach Navigation Center lease. Unmasked conflict of interest under § 1090.',
        'maltego_node_id': 'MAL-NODE-OC-0192',
        'maltego_cli_log': 'maltego-cli --transform EntityUnmask --target "Oliver Chi" --depth 3',
        'maltego_desktop_graph': 'Maltego Desktop View: Entity [Oliver Chi] connected to [Yamada Trust]',
        'maltego_desktop_mtgx_file': 'maltego_exports/oliver_chi_investigation_v1.mtgx',
        'maltego_graph_json': '{"nodes": ["Oliver Chi", "City of HB", "Yamada Living Trust"], "edges": ["Lease Negotiator"]}',
        'mounted_git_repos': ['https://github.com/Tonypost949/OsintNeoAi']
    },

    # 2. PAGE TYPE: STORY / INVESTIGATIVE CASE (HB Navigation Center $14.2M Audit)
    {
        'id': 'hb-navigation-center-investigation',
        'page_type': 'STORY',
        'type_icon': '📰',
        'full_name': 'Investigation: $14.2M Navigation Center Lease & Toxic Soil Capping',
        'initials': 'STORY-HB01',
        'official_title': 'Flagship Municipal Real Estate Lease Audit',
        'agency': 'City of Huntington Beach / Orange County Health Dept',
        'risk_score': 10,
        'risk_level': 'CRITICAL (Public Health & Financial Waste)',
        'category_badge': 'INVESTIGATIVE STORY',
        'category_class': 'cat-story',
        'governing_statutes': ['Cal. Gov. Code § 1090', 'Cal. Civ. Code § 1668', 'Prop 65', 'CEQA'],
        'surety_bond': 'Cal. Civ. Code § 9550 Public Works Bond',
        'whistleblower_payout_rule': '31 U.S.C. § 3730 Qui Tam Relator Payout + 14,200 TFT Reward',
        'dossier_summary': 'Full investigative story unmasking the 10-year shelter lease on 17631 Cameron & 17642 Beach, including illegal 1-year asphalt cap over toxic Hexavalent Chromium soil.',
        'maltego_node_id': 'MAL-NODE-STORY-001',
        'maltego_cli_log': 'maltego-cli --transform StoryMap --target "HB Shelter Audit"',
        'maltego_desktop_graph': 'Maltego Desktop View: Story Node [Navigation Center Audit] -> Edges [Chi], [Yamada Trust], [DTSC]',
        'maltego_desktop_mtgx_file': 'maltego_exports/story_hb_navigation_center.mtgx',
        'maltego_graph_json': '{"nodes": ["Story: Navigation Center", "Hexavalent Chromium", "§ 1090 Disgorgement"], "edges": ["Audited"]}',
        'mounted_git_repos': ['https://github.com/Tonypost949/OsintNeoAi', 'https://github.com/Tonypost949/TaxFundedEngine']
    },

    # 3. PAGE TYPE: ASSET / REAL ESTATE (17631 Cameron Lane Parcel)
    {
        'id': 'asset-17631-cameron-lane',
        'page_type': 'ASSET',
        'type_icon': '🏢',
        'full_name': 'Asset: 17631 Cameron Lane (APN 153-081-02)',
        'initials': 'ASSET-CAMERON',
        'official_title': 'Commercial Real Estate & Shelter Leasehold Asset',
        'agency': 'Orange County Assessor / Shigeru Yamada Trust',
        'risk_score': 9,
        'risk_level': 'CRITICAL (Contaminated Soil & Fraudulent Leasehold)',
        'category_badge': 'REAL ESTATE ASSET',
        'category_class': 'cat-asset',
        'governing_statutes': ['Cal. Health & Safety Code § 25249.6 (Prop 65)', 'Section 214 Welfare Exemption'],
        'surety_bond': 'Title Insurance & Performance Bond Claim',
        'whistleblower_payout_rule': 'California False Claims Act 33% Share on Asset Disgorgement',
        'dossier_summary': 'Property asset containing 22,400 sq ft commercial parcel leased for municipal shelter. High data density asset page.',
        'maltego_node_id': 'MAL-NODE-ASSET-08102',
        'maltego_cli_log': 'maltego-cli --transform AssetLookup --apn "153-081-02"',
        'maltego_desktop_graph': 'Maltego Desktop View: Asset Node [APN 153-081-02] -> Edge [Environmental Risk]',
        'maltego_desktop_mtgx_file': 'maltego_exports/asset_17631_cameron_v1.mtgx',
        'maltego_graph_json': '{"nodes": ["APN 153-081-02", "17631 Cameron Ln", "$4,850,000 Valuation"], "edges": ["Asset Record"]}',
        'mounted_git_repos': ['https://github.com/Tonypost949/OsintNeoAi']
    }
]

os.makedirs('wiki_pages', exist_ok=True)
os.makedirs('maltego_exports', exist_ok=True)

for p in page_types_database:
    # Generate empty .mtgx file
    with open(p['maltego_desktop_mtgx_file'], 'w', encoding='utf-8') as mf:
        mf.write(f"<!-- Maltego Export for Page Type [{p['page_type']}] - {p['full_name']} -->\n" + p['maltego_graph_json'])

    filename = f"wiki_pages/{p['id']}.html"
    repos_html = "".join([f"<li><a href='{r}' target='_blank' style='color: #58a6ff;'>{r}</a></li>" for r in p['mounted_git_repos']])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Wiki Page [{p['page_type']}]: {p['full_name']}</title>
  <style>
    body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 24px; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; max-width: 1100px; margin: auto; }}
    h1 {{ color: #58a6ff; margin-top: 0; display: flex; justify-content: space-between; align-items: center; }}
    .page-type-tag {{ background: #374151; color: #f3f4f6; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-right: 8px; }}
    .badge {{ padding: 6px 12px; border-radius: 20px; font-weight: bold; background: #7f1d1d; color: #fca5a5; font-size: 12px; display: inline-block; }}
    .cat-badge {{ padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px; text-transform: uppercase; margin-left: 8px; }}
    .cat-rico {{ background: #991b1b; color: #fecaca; }}
    .cat-story {{ background: #1e3a8a; color: #93c5fd; }}
    .cat-asset {{ background: #065f46; color: #a7f3d0; }}
    .section-title {{ border-bottom: 1px solid #30363d; padding-bottom: 6px; color: #f0f6fc; margin-top: 24px; font-size: 16px; font-weight: bold; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }}
    th, td {{ border: 1px solid #30363d; padding: 10px; text-align: left; }}
    th {{ background: #21262d; color: #8b949e; width: 30%; }}
    .reward-box {{ background: #064e3b; border: 1px solid #10b981; border-radius: 6px; padding: 14px; color: #a7f3d0; margin-top: 16px; font-size: 13px; }}
    .terminal-box {{ background: #000; border: 1px solid #30363d; border-radius: 6px; padding: 12px; font-family: monospace; color: #00ff66; font-size: 11px; white-space: pre-wrap; margin-top: 10px; }}
    .desktop-box {{ background: #1a1e24; border: 1px solid #3b82f6; border-radius: 6px; padding: 12px; color: #93c5fd; font-size: 12px; margin-top: 10px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>
      <span><span class="page-type-tag">{p['type_icon']} PAGE TYPE: {p['page_type']}</span> {p['full_name']}</span>
      <span class="cat-badge {p['category_class']}">{p['category_badge']}</span>
    </h1>
    <div class="badge">Risk Score: {p['risk_score']}/10 - {p['risk_level']}</div>

    <div class="reward-box">
      🛡️ <strong>Whistleblower & Anti-Fraud Protection Rule:</strong> {p['whistleblower_payout_rule']}
    </div>

    <div class="section-title">📌 Attributes & Page Classification</div>
    <table>
      <tr><th>Page Type Architecture</th><td><strong>{p['page_type']} Page</strong></td></tr>
      <tr><th>Official Title / Name</th><td>{p['official_title']}</td></tr>
      <tr><th>Agency / Entity Association</th><td>{p['agency']}</td></tr>
      <tr><th>Governing Statutes</th><td>{', '.join(p['governing_statutes'])}</td></tr>
      <tr><th>Surety Bond Reference</th><td>{p['surety_bond']}</td></tr>
      <tr><th>TaxFunded Ledger Status</th><td>{p.get('taxfunded_status', 'AUTO_TRANSFERRED')}</td></tr>
      <tr><th>Dossier Summary</th><td>{p['dossier_summary']}</td></tr>
    </table>

    <div class="section-title">💻 Maltego CLI Terminal Output (Headless Automation)</div>
    <div class="terminal-box">$ {p['maltego_cli_log']}</div>

    <div class="section-title">🖥️ Maltego Desktop GUI View & Downloadable Export</div>
    <div class="desktop-box">
      🖥️ <strong>Maltego Desktop Graph View:</strong> {p['maltego_desktop_graph']}<br>
      📁 <strong>Export (.mtgx File):</strong> <a href="../{p['maltego_desktop_mtgx_file']}" style="color: #60a5fa;" download>{p['maltego_desktop_mtgx_file']}</a>
    </div>

    <div class="section-title">⚙️ Mounted GitHub Repositories</div>
    <div style="background: #21262d; border: 1px solid #30363d; padding: 12px; border-radius: 6px; margin-top: 10px;">
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
    print(f"[+] Generated Dedicated Wiki Page [{p['page_type']}]: {filename}")
