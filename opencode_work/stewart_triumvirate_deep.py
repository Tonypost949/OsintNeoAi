from google.cloud import bigquery
import zipfile, os

# 1. GeoTracker check
zpath = r'G:\DL BACKUP\GeoTrackerPermittedUST.zip'
if os.path.exists(zpath):
    with zipfile.ZipFile(zpath) as z:
        for fname in ['permitted_ust.txt', 'permitted_ust_tanks.txt']:
            with z.open(fname) as f:
                content = f.read().decode('latin-1', errors='replace')
                for kw in ['BOUNTY', 'BROOKHURST', 'STEWART', 'TRIUMVIRATE']:
                    if kw in content.upper():
                        lines = content.split('\n')
                        for line in lines:
                            if kw in line.upper():
                                print(f'GeoTracker [{fname}] {kw}: {line[:200]}')
        print()

# 2. PPP check
client = bigquery.Client(project='noble-beanbag-497411-m4')
for name in ['TRIUMVIRATE', 'STEWART']:
    for table_name in ['ppp_150k_plus', 'ppp_up_to_150k']:
        table_ref = f'noble-beanbag-497411-m4.ppp_rico.{table_name}'
        q = f"SELECT BorrowerName, BorrowerCity, BorrowerState, CurrentApprovalAmount, LoanStatus, ForgivenessAmount, DateApproved, JobsReported, BusinessType FROM `{table_ref}` WHERE UPPER(BorrowerName) LIKE '%{name}%' ORDER BY CurrentApprovalAmount DESC LIMIT 5"
        rows = list(client.query(q).result())
        if rows:
            print(f'[ppp_rico.{table_name}] {name}:')
            for r in rows:
                f = f'${r.ForgivenessAmount:,.0f}' if r.ForgivenessAmount else 'N/A'
                print(f'  ${r.CurrentApprovalAmount:,.0f} | {r.BorrowerName} | {r.BorrowerCity}, {r.BorrowerState} | Status: {r.LoanStatus} | Forgiven: {f} | Date: {r.DateApproved}')

# 3. Check rico_evidence_matrix for Stewart/Triumvirate
for table_name in ['rico_evidence_matrix', 'rico_matches', 'suspicious_hb_network']:
    try:
        table_ref = f'noble-beanbag-497411-m4.ppp_rico.{table_name}'
        schema = client.get_table(table_ref).schema
        str_cols = [c.name for c in schema if c.field_type == 'STRING']
        for name in ['STEWART', 'TRIUMVIRATE']:
            conditions = ' OR '.join([f"UPPER(CAST(`{c}` AS STRING)) LIKE '%{name}%'" for c in str_cols[:6]])
            q = f"SELECT * FROM `{table_ref}` WHERE {conditions} LIMIT 5"
            rows = list(client.query(q).result())
            if rows:
                print(f'\n[{table_name}] {name}: {len(rows)} match(es)')
                for r in rows[:3]:
                    d = {k: str(v)[:100] for k, v in dict(r).items() if v}
                    print(f'  {d}')
    except:
        pass

print('\nDone.')
