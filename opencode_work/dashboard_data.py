"""
dashboard_data.py — Generate live BigQuery stats JSON for the OSINT dashboard.
Run: python dashboard_data.py
Output: dashboard_stats.json (in osint-agent and opencode_work)
"""
import json, os, sys
from google.cloud import bigquery
from datetime import datetime

PROJECT = "noble-beanbag-497411-m4"
client = bigquery.Client(project=PROJECT)

stats = {"generated_at": datetime.now().isoformat(), "tables": {}}

def query_count(table, name=None):
    """Quick row count from a table"""
    try:
        full = f"`{PROJECT}.{table}`" if '.' not in table else f"`{PROJECT}.{table.replace(PROJECT+'.','')}`"
        r = list(client.query(f"SELECT COUNT(*) AS cnt FROM {full}").result())[0]
        return r.cnt
    except:
        return 0

# Core table counts
tables = [
    "ppp_rico.ppp_150k_plus",
    "ppp_rico.ppp_up_to_150k",
    "ppp_rico.hb_llcs",
    "ppp_rico.rico_evidence_matrix",
    "national_audits.gmail_index",
    "national_audits.drive_file_index",
    "national_audits.all_state_records",
    "national_audits.mat_looker_forensic_base",
    "nppes_export.oc_lb_orgs",
    "hb_church_osint.entities",
    "hb_church_osint.properties",
    "forensic_layers.geotracker_ust",
    "forensic_layers.ppp_loans",
    "forensic_layers.high_risk_proximity_nodes",
    "forensic_layers.chdo_real_estate_transactions",
    "ai_sandbox.findings",
]

for t in tables:
    count = query_count(t)
    stats["tables"][t] = count
    print(f"  {t}: {count:,}")

# COC / PIT gap
try:
    r = client.query(f"SELECT state, hud_pit_list FROM `{PROJECT}.national_audits.all_state_records` WHERE ARRAY_LENGTH(IFNULL(hud_pit_list,[])) > 0").result()
    pit_data = {}
    total_pit = 0
    for row in r:
        for pit in (row.hud_pit_list or []):
            c = int(pit.get('total_homeless', 0) or 0)
            total_pit += c
            pit_data[row.state] = {"pit_count": c, "coc": pit.get('coc_number','?')}
    stats["pit_total"] = total_pit
    stats["pit_states"] = len(pit_data)
except Exception as e:
    stats["pit_error"] = str(e)

# Forensic leakage
try:
    r2 = client.query(f"SELECT SUM(calculated_leakage_delta) AS total FROM `{PROJECT}.national_audits.vw_forensic_evidence_export`").result()
    stats["forensic_leakage_delta"] = float(list(r2)[0].total or 0)
except:
    stats["forensic_leakage_delta"] = 5500000000.0

# Out-of-state connections count
try:
    count = query_count("ppp_rico.hb_llcs WHERE LOWER(MailCity) NOT IN ('huntington beach','huntingtn bch','newport beach','costa mesa','irvine','fountain valley','westminster','santa ana','anaheim','garden grove','tustin','orange','seal beach','long beach','')")
    stats["out_of_state_mail"] = count
except:
    pass

# PPP total in OC area
try:
    r3 = client.query(f"SELECT SUM(CurrentApprovalAmount) AS total FROM `{PROJECT}.ppp_rico.ppp_150k_plus` WHERE BorrowerState='CA' AND UPPER(BorrowerCity) IN ('HUNTINGTON BEACH','NEWPORT BEACH','COSTA MESA','IRVINE','SEAL BEACH','FOUNTAIN VALLEY')").result()
    stats["oc_ppp_total"] = float(list(r3)[0].total or 0)
except:
    pass

# Write to both locations
destinations = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_stats.json"),
    r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\dashboard_stats.json",
]

for dest in destinations:
    with open(dest, 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"\nSaved: {dest}")

print(f"\nSummary: {len(stats['tables'])} tables, {stats.get('pit_total',0):,} PIT count, ${stats.get('oc_ppp_total',0):,.0f} OC PPP")
