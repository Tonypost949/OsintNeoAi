import csv

# Search for all entities at 7561 Center Ave
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_rico_hb_llcs.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    print('=== ALL ENTITIES AT 7561 CENTER AVE ===')
    for row in reader:
        if '7561 CENTER' in (row.get('SiteAddress', '') or '').upper():
            print(f"  Owner: {row.get('Owner1','')} | Unit: {row.get('SiteAddress','')} | Mail: {row.get('MailAddress','')} | Seller: {row.get('LastSeller','')} | Sale: {row.get('LastSaleDate','')} / ${row.get('LastSaleValue','')}")
            print()

# DYLAN & ANDREW HOLDINGS
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_rico_hb_llcs.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    print('=== DYLAN & ANDREW HOLDINGS ===')
    for row in reader:
        if 'DYLAN' in (row.get('Owner1', '') or '').upper():
            print(f"  Owner: {row.get('Owner1','')} | Address: {row.get('SiteAddress','')} | Mail: {row.get('MailAddress','')} | MailCity: {row.get('MailCity','')} | Seller: {row.get('LastSeller','')} | Sale: {row.get('LastSaleDate','')} / ${row.get('LastSaleValue','')} | APN: {row.get('APN','')}")
            print()

# TAM NGUYEN / GGCF
for f in ['ppp_rico_ppp_150k_plus.csv', 'ppp_rico_ppp_up_to_150k.csv']:
    try:
        with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\\' + f, 'r', encoding='utf-8') as cf:
            reader = csv.DictReader(cf)
            for row in reader:
                name = (row.get('BorrowerName', '') or '').upper()
                if 'TAM NGUYEN' in name or 'GARDEN GROVE COMMUNITY' in name:
                    print(f'=== TAM NGUYEN/GGCF PPP [{f}] ===')
                    print(f"  Borrower: {row.get('BorrowerName','')}")
                    print(f"  City: {row.get('BorrowerCity','')} | State: {row.get('BorrowerState','')}")
                    print(f"  Amount: ${row.get('CurrentApprovalAmount','')}")
                    print(f"  NAICS: {row.get('NAICSCode','')} | Jobs: {row.get('JobsReported','')}")
                    print(f"  Date: {row.get('DateApproved','')} | Status: {row.get('LoanStatus','')}")
                    print(f"  Address: {row.get('BorrowerAddress','')}")
                    print()
    except Exception as e:
        print(f'{f}: {e}')

# Search Haynes-Do connection
for f_name in ['national_audits_mat_looker_forensic_base.csv', 'mat_looker_forensic_base.csv']:
    try:
        with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\\' + f_name, 'r', encoding='utf-8') as cf:
            reader = csv.DictReader(cf)
            for row in reader:
                text = ' '.join([str(v) for v in row.values() if v])
                if 'LARRY HAYNES' in text.upper() or 'ANDREW DO' in text.upper():
                    print(f'=== HAYNES/DO LINK [{f_name}] ===')
                    for k, v in row.items():
                        if v:
                            print(f"  {k}: {v[:200]}")
                    print()
    except Exception as e:
        pass

# ICWA/IIM in evidence chain of custody
try:
    with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_evidence_chain_of_custody.csv', 'r', encoding='utf-8') as cf:
        reader = csv.DictReader(cf)
        for row in reader:
            text = ' '.join([str(v) for v in row.values() if v])
            if 'ICWA' in text.upper() or 'IIM' in text.upper() or 'INDIAN' in text.upper() or 'TRIBAL' in text.upper():
                print('=== ICWA/IIM IN EVIDENCE CHAIN ===')
                for k, v in row.items():
                    if v:
                        print(f"  {k}: {v[:200]}")
                print()
except Exception as e:
    print(f'evidence_chain: {e}')
