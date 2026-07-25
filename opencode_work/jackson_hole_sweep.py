from google.cloud import bigquery
import json

client = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== BANK OF JACKSON HOLE TRUST — FULL LENDER SWEEP ===\n")

for table_name in ['ppp_150k_plus', 'ppp_up_to_150k']:
    ppp_table = f'noble-beanbag-497411-m4.ppp_rico.{table_name}'
    
    # Full sweep
    q = f"""
    SELECT 
        BorrowerName, BorrowerCity, BorrowerState, BorrowerAddress,
        InitialApprovalAmount, CurrentApprovalAmount, DateApproved,
        LoanStatus, ForgivenessAmount, JobsReported, NAICSCode,
        BusinessType, OriginatingLender, OriginatingLenderCity, OriginatingLenderState,
        ProjectCity, ProjectState, ProcessingMethod, Term
    FROM `{ppp_table}`
    WHERE UPPER(OriginatingLender) LIKE '%JACKSON HOLE%'
    ORDER BY CurrentApprovalAmount DESC
    """
    rows = list(client.query(q).result())
    print(f"[{table_name}] Total Jackson Hole loans: {len(rows)}\n")
    
    if not rows:
        continue
    
    totals = {
        'count': len(rows),
        'total_amount': sum(r.CurrentApprovalAmount or 0 for r in rows),
        'total_forgiven': sum(r.ForgivenessAmount or 0 for r in rows),
        'total_jobs': sum(r.JobsReported or 0 for r in rows),
    }
    print(f"  Aggregate: {totals['total_amount']:,.0f} total / {totals['total_forgiven']:,.0f} forgiven / {totals['total_jobs']} jobs\n")
    
    # Geographic summary
    states = {}
    cities = {}
    for r in rows:
        s = r.BorrowerState or '??'
        c = r.BorrowerCity or '??'
        states[s] = states.get(s, 0) + 1
        cities[c] = cities.get(c, 0) + 1
    
    print(f"  States: {len(states)}")
    for s, c in sorted(states.items(), key=lambda x: -x[1])[:10]:
        print(f"    {s}: {c}")
    print(f"  Cities: {len(cities)}")
    for c, n in sorted(cities.items(), key=lambda x: -x[1])[:15]:
        print(f"    {c}: {n}")
    
    # Full rows
    print(f"\n  === ALL LOANS ===")
    for r in rows:
        key = {
            'name': r.BorrowerName[:60],
            'city': r.BorrowerCity,
            'state': r.BorrowerState,
            'amount': f"${r.CurrentApprovalAmount:,.0f}" if r.CurrentApprovalAmount else None,
            'date': r.DateApproved,
            'status': r.LoanStatus,
            'forgiven': f"${r.ForgivenessAmount:,.0f}" if r.ForgivenessAmount else None,
            'jobs': r.JobsReported,
            'naics': r.NAICSCode,
            'type': r.BusinessType,
            'project': f"{r.ProjectCity}, {r.ProjectState}",
        }
        print(f"    {json.dumps(key)}")
    print()

# CA-only sweep
print("=== CA-SPECIFIC SWEEP ===\n")
for table_name in ['ppp_150k_plus', 'ppp_up_to_150k']:
    ppp_table = f'noble-beanbag-497411-m4.ppp_rico.{table_name}'
    q = f"""
    SELECT 
        BorrowerName, BorrowerCity, BorrowerState, BorrowerAddress,
        CurrentApprovalAmount, DateApproved, LoanStatus, ForgivenessAmount,
        JobsReported, NAICSCode, BusinessType, ProjectCity, ProjectState
    FROM `{ppp_table}`
    WHERE UPPER(OriginatingLender) LIKE '%JACKSON HOLE%'
      AND (
        UPPER(BorrowerState) = 'CA'
        OR UPPER(BorrowerCity) LIKE '%HUNTINGTON%'
        OR UPPER(BorrowerCity) LIKE '%FOUNTAIN%'
        OR UPPER(BorrowerCity) LIKE '%SEAL%'
        OR UPPER(BorrowerCity) LIKE '%NEWPORT%'
        OR UPPER(BorrowerCity) LIKE '%COSTA MESA%'
        OR UPPER(BorrowerCity) LIKE '%IRVINE%'
      )
    ORDER BY CurrentApprovalAmount DESC
    """
    rows = list(client.query(q).result())
    print(f"[{table_name}] CA/HB-linked loans: {len(rows)}")
    for r in rows:
        print(f"  ${r.CurrentApprovalAmount:,.0f} | {r.BorrowerName[:50]} | {r.BorrowerCity}, {r.BorrowerState} | NAICS: {r.NAICSCode} | Jobs: {r.JobsReported} | {r.LoanStatus}")

print("\nDone.")
