import requests

ein = '952274613'
url = f'https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json'
r = requests.get(url)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    org = data.get('organization', {})
    print(f"Name: {org.get('name')}")
    print(f"EIN: {org.get('ein')}")
    print(f"Address: {org.get('address')}")
    print(f"Tax period: {org.get('tax_period')}")
    print(f"Revenue: {org.get('total_revenue')}")
    
    filings = data.get('filings_with_data', {}).get('filings', [])
    print(f"\nFilings with data: {len(filings)}")
    for f in filings[:3]:
        print(f"  Year: {f.get('tax_prd_yr')}, Revenue: {f.get('total_revenue')}, Expenses: {f.get('total_expenses')}")
else:
    print(r.text[:500])
