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
        'maltego_cli_log': 'maltego-cli --transform EntityUnmask --target "Oliver Chi" --depth 3\n[+] CLI Output: Linked 4 entities via local transform script',
        'maltego_desktop_graph': 'Maltego CE / XL Graph View: Entity [Oliver Chi] connected to [Shigeru Yamada Trust], [Mitsuru Yamada Trust], and [City Council Resolution 2020-41]',
        'maltego_desktop_mtgx_file': 'maltego_exports/oliver_chi_investigation_v1.mtgx',
        'maltego_graph_json': '{"nodes": ["Oliver Chi", "City of HB", "Yamada Living Trust"], "edges": ["Lease Negotiator", "Financial Interest"]}',
        'mounted_git_repos': ['https://github.com/Tonypost949/OsintNeoAi', 'https://github.com/Tonypost949/TaxFundedEngine'],
        
        # High Real Estate Data Density Sections
        'real_estate_parcels': [
            {'apn': '153-081-02', 'address': '17631 Cameron Lane, Huntington Beach, CA 92647', 'land_use': 'Commercial / Homeless Shelter Lease', 'sq_ft': '22,400 sq ft', 'assessed_val': '$4,850,000 USD', 'zoning': 'CG (General Commercial)', 'owner_of_record': 'Shigeru Yamada Living Trust'},
            {'apn': '153-081-05', 'address': '17642 Beach Blvd, Huntington Beach, CA 92647', 'land_use': 'Commercial Real Estate / Asphalt Cap Site', 'sq_ft': '18,600 sq ft', 'assessed_val': '$3,950,000 USD', 'zoning': 'CG (General Commercial)', 'owner_of_record': 'Mitsuru Yamada Living Trust'}
        ],
        'deed_transfers': [
            {'grantor': 'Yamada Family Trust', 'grantee': 'Shigeru Yamada Trustee', 'doc_num': '2019-00048192', 'date': '2019-03-14', 'transfer_tax': '$0.00 (Exempt Trust Transfer)'},
            {'grantor': 'Shigeru Yamada Trustee', 'grantee': 'City of Huntington Beach (Leasehold)', 'doc_num': '2020-00019284', 'date': '2020-06-22', 'transfer_tax': '$14,200,000 Lease Valuation'}
        ],
        'gis_coordinates': {'lat': 33.7042, 'lon': -117.9889, 'elevation': '38 ft', 'parcel_boundary_polygon': 'POLYGON((-117.9892 33.7045, -117.9886 33.7045, -117.9886 33.7039, -117.9892 33.7039))'},
        'environmental_records': {'soil_contaminant': 'Hexavalent Chromium (Cr VI)', 'soil_depth': '0 - 4 ft below grade', 'capping_status': '1-Year Asphalt Cap (Defective Warranty)', 'water_board_id': 'RB8-2020-0012'},
        'tax_records': {'annual_property_tax': '$58,410.22', 'tax_exemption_claimed': 'Welfare Exemption (Section 214)', 'exemption_status': 'UNDER AUDIT / REVOCATION PENDING'}
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
        'maltego_cli_log': 'maltego-cli --transform ParcelLookup --target "17631 Cameron Ln"\n[+] CLI Output: Soil capping defect flagged (Hexavalent Chromium)',
        'maltego_desktop_graph': 'Maltego Desktop UI: Graph Entity [Shigeru Yamada] -> Edge [Property Lease] -> [17631 Cameron Ln]',
        'maltego_desktop_mtgx_file': 'maltego_exports/shigeru_yamada_parcel_v1.mtgx',
        'maltego_graph_json': '{"nodes": ["Shigeru Yamada", "17631 Cameron Ln", "Hexavalent Chromium Risk"], "edges": ["Trustee", "Soil Capping"]}',
        'mounted_git_repos': ['https://github.com/Tonypost949/OsintNeoAi'],
        
        'real_estate_parcels': [
            {'apn': '153-081-02', 'address': '17631 Cameron Lane, Huntington Beach, CA 92647', 'land_use': 'Commercial / Homeless Shelter Lease', 'sq_ft': '22,400 sq ft', 'assessed_val': '$4,850,000 USD', 'zoning': 'CG (General Commercial)', 'owner_of_record': 'Shigeru Yamada Living Trust'}
        ],
        'deed_transfers': [
            {'grantor': 'Yamada Family Trust', 'grantee': 'Shigeru Yamada Trustee', 'doc_num': '2019-00048192', 'date': '2019-03-14', 'transfer_tax': '$0.00 (Exempt Trust Transfer)'}
        ],
        'gis_coordinates': {'lat': 33.7042, 'lon': -117.9889, 'elevation': '38 ft', 'parcel_boundary_polygon': 'POLYGON((-117.9892 33.7045, -117.9886 33.7045, -117.9886 33.7039, -117.9892 33.7039))'},
        'environmental_records': {'soil_contaminant': 'Hexavalent Chromium (Cr VI)', 'soil_depth': '0 - 4 ft below grade', 'capping_status': '1-Year Asphalt Cap (Defective Warranty)', 'water_board_id': 'RB8-2020-0012'},
        'tax_records': {'annual_property_tax': '$58,410.22', 'tax_exemption_claimed': 'Welfare Exemption (Section 214)', 'exemption_status': 'UNDER AUDIT / REVOCATION PENDING'}
    }
]

os.makedirs('wiki_pages', exist_ok=True)

for e in entities:
    filename = f"wiki_pages/{e['id']}.html"
    repos_html = "".join([f"<li><a href='{r}' target='_blank' style='color: #58a6ff;'>{r}</a></li>" for r in e['mounted_git_repos']])
    
    parcels_html = "".join([f"""
    <tr>
      <td><strong>{p['apn']}</strong></td>
      <td>{p['address']}</td>
      <td>{p['land_use']}</td>
      <td>{p['sq_ft']}</td>
      <td>{p['assessed_val']}</td>
      <td>{p['zoning']}</td>
      <td>{p['owner_of_record']}</td>
    </tr>
    """ for p in e.get('real_estate_parcels', [])])

    deeds_html = "".join([f"""
    <tr>
      <td>{d['doc_num']}</td>
      <td>{d['date']}</td>
      <td>{d['grantor']}</td>
      <td>{d['grantee']}</td>
      <td>{d['transfer_tax']}</td>
    </tr>
    """ for d in e.get('deed_transfers', [])])

    gis = e.get('gis_coordinates', {})
    env = e.get('environmental_records', {})
    tax = e.get('tax_records', {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Wiki Entry: {e['full_name']} ({e['initials']}) - High Data Density Profile</title>
  <style>
    body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 24px; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; max-width: 1200px; margin: auto; }}
    h1 {{ color: #58a6ff; margin-top: 0; display: flex; justify-content: space-between; align-items: center; }}
    .badge {{ padding: 6px 12px; border-radius: 20px; font-weight: bold; background: #7f1d1d; color: #fca5a5; font-size: 12px; display: inline-block; }}
    .cat-badge {{ padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px; text-transform: uppercase; margin-left: 8px; }}
    .cat-rico {{ background: #991b1b; color: #fecaca; }}
    .section-title {{ border-bottom: 1px solid #30363d; padding-bottom: 6px; color: #f0f6fc; margin-top: 24px; font-size: 16px; font-weight: bold; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 12px; }}
    th, td {{ border: 1px solid #30363d; padding: 8px 10px; text-align: left; }}
    th {{ background: #21262d; color: #8b949e; }}
    .grid-density {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 12px; }}
    .sub-card {{ background: #1c2128; border: 1px solid #30363d; border-radius: 6px; padding: 12px; }}
    .sub-card h4 {{ margin: 0 0 8px 0; color: #58a6ff; font-size: 13px; border-bottom: 1px solid #30363d; padding-bottom: 4px; }}
    .terminal-box {{ background: #000; border: 1px solid #30363d; border-radius: 6px; padding: 12px; font-family: monospace; color: #00ff66; font-size: 11px; white-space: pre-wrap; margin-top: 10px; }}
    .desktop-box {{ background: #1a1e24; border: 1px solid #3b82f6; border-radius: 6px; padding: 12px; color: #93c5fd; font-size: 12px; margin-top: 10px; }}
    .graph-box {{ background: #1f2937; border: 1px solid #374151; border-radius: 6px; padding: 12px; margin-top: 10px; font-family: monospace; color: #9ca3af; font-size: 11px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>
      <span>👤 {e['full_name']} ({e['initials']})</span>
      <span class="cat-badge {e['category_class']}">{e['category_badge']}</span>
    </h1>
    <div class="badge">Risk Score: {e['risk_score']}/10 - {e['risk_level']}</div>

    <div class="section-title">📌 Attributes & Profile Metadata</div>
    <table>
      <tr><th style="width: 25%;">Category Classification</th><td><strong style="color: #fca5a5;">{e['investigative_category']}</strong></td></tr>
      <tr><th>Official Title</th><td>{e['official_title']}</td></tr>
      <tr><th>Agency / Entity</th><td>{e['agency']}</td></tr>
      <tr><th>Governing Statutes</th><td>{', '.join(e['governing_statutes'])}</td></tr>
      <tr><th>Surety Bond Status</th><td>{e['surety_bond']}</td></tr>
      <tr><th>TaxFunded Ledger</th><td>{e['taxfunded_status']}</td></tr>
    </table>

    <div class="section-title">🏢 High-Density Real Estate Parcel Directory (APN & Property Assets)</div>
    <table>
      <thead>
        <tr>
          <th>APN (Parcel #)</th>
          <th>Situs Address</th>
          <th>Land Use / Purpose</th>
          <th>Square Feet</th>
          <th>Assessed Value</th>
          <th>Zoning</th>
          <th>Owner of Record</th>
        </tr>
      </thead>
      <tbody>
        {parcels_html}
      </tbody>
    </table>

    <div class="section-title">📜 County Recorder Deed Transfers & Title Documents</div>
    <table>
      <thead>
        <tr>
          <th>Doc Number</th>
          <th>Recording Date</th>
          <th>Grantor (Seller/Transferor)</th>
          <th>Grantee (Buyer/Recipient)</th>
          <th>Transfer Tax / Value</th>
        </tr>
      </thead>
      <tbody>
        {deeds_html}
      </tbody>
    </table>

    <div class="section-title">🗺️ High-Density GIS, Environmental & Property Tax Data Grid</div>
    <div class="grid-density">
      <div class="sub-card">
        <h4>🗺️ GIS Coordinates & Boundaries</h4>
        <div><strong>Latitude:</strong> {gis.get('lat', 'N/A')}</div>
        <div><strong>Longitude:</strong> {gis.get('lon', 'N/A')}</div>
        <div><strong>Elevation:</strong> {gis.get('elevation', 'N/A')}</div>
        <div style="font-size: 10px; font-family: monospace; color: #8b949e; margin-top: 4px;">{gis.get('parcel_boundary_polygon', 'N/A')}</div>
      </div>
      <div class="sub-card">
        <h4>🧪 Environmental Hazard Audit</h4>
        <div><strong>Contaminant:</strong> {env.get('soil_contaminant', 'N/A')}</div>
        <div><strong>Depth:</strong> {env.get('soil_depth', 'N/A')}</div>
        <div><strong>Cap Status:</strong> {env.get('capping_status', 'N/A')}</div>
        <div><strong>Water Board ID:</strong> {env.get('water_board_id', 'N/A')}</div>
      </div>
      <div class="sub-card">
        <h4>💰 Tax Assessor & Exemption Audit</h4>
        <div><strong>Annual Tax:</strong> {tax.get('annual_property_tax', 'N/A')}</div>
        <div><strong>Exemption Claimed:</strong> {tax.get('tax_exemption_claimed', 'N/A')}</div>
        <div><strong>Status:</strong> <strong style="color: #ef4444;">{tax.get('exemption_status', 'N/A')}</strong></div>
      </div>
    </div>

    <div class="section-title">💻 Maltego CLI Terminal Output (Headless Automation)</div>
    <div class="terminal-box">$ {e['maltego_cli_log']}</div>

    <div class="section-title">🖥️ Maltego Desktop GUI View & Downloadable Graph Export</div>
    <div class="desktop-box">
      🖥️ <strong>Maltego Desktop Graph View:</strong> {e['maltego_desktop_graph']}<br>
      📁 <strong>Export (.mtgx File):</strong> <a href="../{e['maltego_desktop_mtgx_file']}" style="color: #60a5fa;" download>{e['maltego_desktop_mtgx_file']}</a>
    </div>

    <div class="section-title">🕸️ Maltego Graph Blueprint (Node #{e['maltego_node_id']})</div>
    <div class="graph-box">JSON Blueprint:<br>{e['maltego_graph_json']}</div>

    <p style="margin-top: 24px;"><a href="../master_wiki_portal.html" style="color: #58a6ff;">← Back to Master Wiki Directory</a></p>
  </div>
</body>
</html>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Expanded High-Density Real Estate Data Wiki Page: {filename}")
