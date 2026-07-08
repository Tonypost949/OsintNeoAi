import csv

print('=== 88 FAIR DR CLUSTER - LOCAL SEARCH ===')
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\ppp_rico_hb_llcs.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        site = (row.get('SiteAddress', '') or '').upper()
        mail = (row.get('MailAddress', '') or '').upper()
        if '88 FAIR' in site or '88 FAIR' in mail:
            count += 1
            owner = row.get('Owner1', '')
            address = row.get('SiteAddress', '')
            mail_addr = row.get('MailAddress', '')
            mail_city = row.get('MailCity', '')
            mail_state = row.get('MailState', '')
            apn = row.get('APN', '')
            seller = row.get('LastSeller', '')
            sale_date = row.get('LastSaleDate', '')
            sale_val = row.get('LastSaleValue', '')
            print(f'{count}. {owner}')
            print(f'   Address: {address}')
            print(f'   Mail: {mail_addr}, {mail_city}, {mail_state}')
            print(f'   APN: {apn}')
            print(f'   Seller: {seller}')
            print(f'   Sale: {sale_date} / ${sale_val}')
            print()
    print(f'Total entities at 88 Fair Dr: {count}')
