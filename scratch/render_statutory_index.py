import json

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OsintNeoAi - Mandatory Legal Data & Statutory Statute Index</title>
  <style>
    body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0b0f19; color: #e2e8f0; padding: 24px; margin: 0; }
    h1 { color: #38bdf8; font-size: 24px; margin-top: 0; }
    h2 { color: #f59e0b; font-size: 18px; margin-top: 16px; border-bottom: 1px solid #334155; padding-bottom: 8px; }
    .mandate-banner { background: #064e3b; border: 1px solid #059669; color: #34d399; padding: 12px 16px; border-radius: 6px; font-weight: bold; margin-bottom: 20px; font-size: 13px; }
    .case-banner { background: #1e1b4b; border: 1px solid #6366f1; color: #c7d2fe; padding: 16px; border-radius: 8px; margin-bottom: 20px; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; margin-bottom: 16px; }
    .statute-tag { background: #0284c7; color: #fff; padding: 3px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; font-weight: bold; }
    .statute-toxic { background: #b91c1c; color: #fff; padding: 3px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; font-weight: bold; }
    .statute-deal { background: #7c3aed; color: #fff; padding: 3px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; font-weight: bold; }
    .statute-fca { background: #d97706; color: #fff; padding: 3px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
    th, td { text-align: left; padding: 12px; border-bottom: 1px solid #334155; }
    th { background: #0f172a; color: #94a3b8; }
    a { color: #38bdf8; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .metric-badge { background: #334155; color: #f8fafc; font-weight: bold; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
  </style>
</head>
<body>
  <div style="max-width: 1200px; margin: 0 auto;">
    <h1>⚖️ Mandatory Legal Data & Statutory Law Index</h1>
    <div class="mandate-banner">
      📜 MANDATORY REPO RULE: Every transaction, public cost, agreement, trade, or physical/environmental risk MUST be statutorily linked to its governing Federal and State legal laws in this Legal Section.
    </div>

    <!-- Active Whistleblower Litigation Feature -->
    <div class="case-banner">
      <h2 style="margin-top: 0; color: #818cf8;">🏛️ Active Federal Whistleblower Litigation: <em>Jesse Knabb v. City of Huntington Beach et al.</em></h2>
      <p style="font-size: 13px; margin: 4px 0 12px 0; color: #94a3b8;">
        <strong>Case Number:</strong> <code>Case No. 8:26-cv-00348-JWH-ADS</code> | 
        <strong>Court:</strong> U.S. District Court, Central District of California (Santa Ana) | 
        <strong>Filed:</strong> February 14, 2026<br/>
        <strong>Presiding Judge:</strong> Hon. John W. Holcomb | 
        <strong>Referring Magistrate Judge:</strong> Hon. Autumn D. Spaeth | 
        <strong>Nature of Suit:</strong> 893 Environmental Matters (42 U.S.C. § 6901 / CERCLA § 9601 / FCA 31 U.S.C. § 3729)
      </p>
      <table>
        <thead>
          <tr>
            <th>Litigation Role</th>
            <th>Entity / Party Name</th>
            <th>Case Standing & Statutory Allegations</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Plaintiff / Relator</strong></td>
            <td><strong style="color: #38bdf8;">Jesse Knabb</strong></td>
            <td>Whistleblower & Pro Se Petitioner residing at Huntington Beach Navigation Center</td>
          </tr>
          <tr>
            <td><strong>Defendant Operator</strong></td>
            <td><strong style="color: #f87171;">Mercy House Living Centers, Inc.</strong></td>
            <td>Operator of Navigation Center ($74.2M SEFA grants, CMS billing contractor, Toxic Exposure & Retaliation)</td>
          </tr>
          <tr>
            <td><strong>Defendant Municipality</strong></td>
            <td><strong>City of Huntington Beach</strong></td>
            <td>Municipal site owner (17631 Cameron & 17642 Beach Blvd contaminated land lease)</td>
          </tr>
          <tr>
            <td><strong>Defendant Environmental Firm</strong></td>
            <td><strong>EEC Environmental</strong></td>
            <td>Site assessor (Hexavalent Chromium Cr-VI testing at 49x statutory safety limits)</td>
          </tr>
          <tr>
            <td><strong>Defendant County Authority</strong></td>
            <td><strong>County of Orange / OCSD</strong></td>
            <td>Pass-through funding authority ($90M CARES Act allocation to Mercy House network)</td>
          </tr>
          <tr>
            <td><strong>Defendant CHDO Shell</strong></td>
            <td><strong>CM Mercy House CHDO LLC / Casa Aliento LP</strong></td>
            <td>Housing shell partnership (Vagabond Inn property acquisition & self-dealing transfer)</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Master Statutory Law Index (LAW-001 to LAW-008) -->
    <div class="card">
      <h3 style="margin-top: 0; color: #38bdf8;">📜 Master Law ID Registry Index (LAW-001 to LAW-008)</h3>
      <table>
        <thead>
          <tr>
            <th>Law ID</th>
            <th>Statute Code & Citation</th>
            <th>Legal Title & Name</th>
            <th>Governing Scope & BigQuery Matches</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>[LAW-001]</strong></td>
            <td><span class="statute-tag">Cal. Gov. Code § 1090</span></td>
            <td><a href="file:///C:/OsintNeoAi/statutory_legal_mapping_registry.json#L6-L10">Prohibition Against Financial Interest in Public Contracts</a></td>
            <td>Applies to all public purchases, land deals, vendor agreements <span class="metric-badge">109 Records</span></td>
          </tr>
          <tr>
            <td><strong>[LAW-002]</strong></td>
            <td><span class="statute-tag">Cal. Gov. Code § 87100</span></td>
            <td><a href="file:///C:/OsintNeoAi/statutory_legal_mapping_registry.json#L11-L15">Political Reform Act (PRA) Conflict & Form 700</a></td>
            <td>Mandates economic interest disclosures by public officials & trusts <span class="metric-badge">62 Records</span></td>
          </tr>
          <tr>
            <td><strong>[LAW-003]</strong></td>
            <td><span class="statute-fca">31 U.S.C. § 3729</span></td>
            <td><a href="file:///C:/OsintNeoAi/statutory_legal_mapping_registry.json#L16-L20">Federal False Claims Act (Qui Tam Action)</a></td>
            <td>Governs fraudulent billing, PPP loan diversion, federal grant fraud <span class="metric-badge">187 Records</span></td>
          </tr>
          <tr>
            <td><strong>[LAW-004]</strong></td>
            <td><span class="statute-toxic">Cal. Health & Safety Code § 25249.5</span></td>
            <td><a href="file:///C:/OsintNeoAi/statutory_legal_index.html#L65-L68">Prop 65 Toxic Chemicals & Carcinogens</a></td>
            <td>Prohibits exposure to Hexavalent Chromium (Cr-VI), lead, toxic dust <span class="metric-badge">118 Records</span></td>
          </tr>
          <tr>
            <td><strong>[LAW-005]</strong></td>
            <td><span class="statute-toxic">Cal. Pub. Res. Code § 21000</span></td>
            <td><a href="file:///C:/OsintNeoAi/statutory_legal_index.html#L69-L72">California Environmental Quality Act (CEQA)</a></td>
            <td>Mandatory environmental impact reports & public health remediation <span class="metric-badge">142 Records</span></td>
          </tr>
          <tr>
            <td><strong>[LAW-006]</strong></td>
            <td><span class="statute-toxic">42 U.S.C. § 9601</span></td>
            <td><a href="file:///C:/OsintNeoAi/statutory_legal_index.html#L70-L74">CERCLA / Superfund Cap Strict Liability</a></td>
            <td>Strict liability for hazardous substance releases & cap maintenance <span class="metric-badge">9 Records</span></td>
          </tr>
          <tr>
            <td><strong>[LAW-007]</strong></td>
            <td><span class="statute-deal">Cal. Gov. Code § 54956.8</span></td>
            <td><a href="file:///C:/OsintNeoAi/statutory_legal_index.html#L91-L95">Brown Act Real Property Negotiation Disclosure</a></td>
            <td>Closed-session real estate deals, public price & negotiator disclosures <span class="metric-badge">34 Records</span></td>
          </tr>
          <tr>
            <td><strong>[LAW-008]</strong></td>
            <td><span class="statute-deal">Cal. Gov. Code § 6250</span></td>
            <td><a href="file:///C:/OsintNeoAi/statutory_legal_index.html#L96-L100">California Public Records Act (CPRA / FOIA)</a></td>
            <td>Guarantees public right to inspect agency contracts, leases, warranties <span class="metric-badge">1 Record</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- BigQuery 439-Record Audit Matrix -->
    <div class="card">
      <h3 style="margin-top: 0; color: #34d399;">📊 BigQuery 439-Record Statutory Audit Summary</h3>
      <p style="font-size: 13px; color: #94a3b8;">
        Target Project: <code>noble-beanbag-497411-m4</code> | Master JSON Log: <a href="file:///C:/OsintNeoAi/data/bigquery_law_id_audit_results.json"><code>data/bigquery_law_id_audit_results.json</code></a>
      </p>
      <table>
        <thead>
          <tr>
            <th>BigQuery Dataset & Table ID</th>
            <th>Governing Law IDs Tagged</th>
            <th>Audit Scope & Case Significance</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>noble-beanbag-497411-m4.forensic_layers.fca_timeline</code></td>
            <td><span class="statute-fca">LAW-003</span> <span class="statute-tag">LAW-001</span></td>
            <td>FCA whistleblower timeline, relator disclosures, CARES Act allocations</td>
          </tr>
          <tr>
            <td><code>noble-beanbag-497411-m4.forensic_layers.chdo_real_estate_transactions</code></td>
            <td><span class="statute-deal">LAW-007</span> <span class="statute-tag">LAW-001</span> <span class="statute-tag">LAW-002</span></td>
            <td>CM Mercy House CHDO & Casa Aliento real estate property transfers</td>
          </tr>
          <tr>
            <td><code>noble-beanbag-497411-m4.forensic_layers.geotracker_ust</code></td>
            <td><span class="statute-toxic">LAW-004</span> <span class="statute-toxic">LAW-005</span> <span class="statute-toxic">LAW-006</span></td>
            <td>Huntington Beach Navigation Center toxic soil contamination (Hexavalent Chromium)</td>
          </tr>
          <tr>
            <td><code>noble-beanbag-497411-m4.national_audits.all_state_records</code></td>
            <td><span class="statute-fca">LAW-003</span> <span class="statute-tag">LAW-001</span> <span class="statute-deal">LAW-008</span></td>
            <td>Master municipal records, public grants, and state contract disclosures</td>
          </tr>
          <tr>
            <td><code>noble-beanbag-497411-m4.onedrive_forensics.onedrive_documents</code></td>
            <td><span class="statute-fca">LAW-003</span> <span class="statute-tag">LAW-001</span> <span class="statute-deal">LAW-007</span></td>
            <td>Forensic document exports, contract agreements, and internal email logs</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""

with open(r"C:\OsintNeoAi\statutory_legal_index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("[+] Successfully rendered rich statutory_legal_index.html!")
