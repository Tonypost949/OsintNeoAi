import csv

# Check WEST CONTINENTAL for all properties
print("=== WEST CONTINENTAL PROPERTIES (all holdings) ===")
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_rico_hb_llcs.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        if 'WEST CONTINENTAL' in (row.get('Owner1','') or '').upper():
            print(f"  Owner: {row.get('Owner1','')}")
            print(f"  SiteAddress: {row.get('SiteAddress','')}")
            print(f"  Mail: {row.get('MailAddress','')}, {row.get('MailCity','')}")
            print(f"  Seller: {row.get('LastSeller','')}")
            print(f"  Sale: {row.get('LastSaleDate','')} / ${row.get('LastSaleValue','')}")
            print(f"  APN: {row.get('APN','')}")
            print()

# GATES as seller in ANY property
print("=== GATES FAMILY (as seller) ===")
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_rico_hb_llcs.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        seller = (row.get('LastSeller','') or '').upper()
        if 'GATES' in seller:
            print(f"  Buyer: {row.get('Owner1','')}")
            print(f"  SiteAddress: {row.get('SiteAddress','')}")
            print(f"  Mail: {row.get('MailAddress','')}, {row.get('MailCity','')}")
            print(f"  Seller: {row.get('LastSeller','')}")
            print(f"  Sale: {row.get('LastSaleDate','')} / ${row.get('LastSaleValue','')}")
            print()

# Chen family as seller
print("=== CHEN FAMILY (as seller of Beach Blvd easement parcels) ===")
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_rico_hb_llcs.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        seller = (row.get('LastSeller','') or '').upper()
        if 'CHEN' in seller:
            print(f"  Buyer: {row.get('Owner1','')}")
            print(f"  SiteAddress: {row.get('SiteAddress','')}")
            print(f"  Mail: {row.get('MailAddress','')}, {row.get('MailCity','')}")
            print(f"  Seller: {row.get('LastSeller','')}")
            print(f"  Sale: {row.get('LastSaleDate','')} / ${row.get('LastSaleValue','')}")
            print()

# Search evidence chain for GATES
print("=== EVIDENCE CHAIN: GATES ===")
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_evidence_chain_of_custody.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        text = ' '.join([str(v) for v in row.values() if v]).upper()
        if 'GATES' in text:
            for k, v in row.items():
                if v: print(f"  {k}: {v[:200]}")
            print()

# Search drive index for GATES
print("=== DRIVE INDEX: GATES ===")
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_drive_file_index.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        name = (row.get('file_name','') or '').upper()
        if 'GATES' in name:
            print(f"  {row.get('file_name','')} | ID: {row.get('file_id','')} | Modified: {row.get('modified_time','')}")

# AFFORDABLE HOUSING LAND CONSULTANTS LLC
print("\n=== AFFORDABLE HOUSING LAND CONSULTANTS ===")
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_rico_hb_llcs.csv', 'r', encoding='utf-8') as cf:
    reader = csv.DictReader(cf)
    for row in reader:
        if 'AFFORDABLE HOUSING' in (row.get('Owner1','') or '').upper():
            print(f"  Owner: {row.get('Owner1','')}")
            print(f"  SiteAddress: {row.get('SiteAddress','')}")
            print(f"  Mail: {row.get('MailAddress','')}, {row.get('MailCity','')}")
            print(f"  Seller: {row.get('LastSeller','')}")
            print(f"  Sale: {row.get('LastSaleDate','')} / ${row.get('LastSaleValue','')}")
            print()
