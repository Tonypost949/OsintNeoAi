import csv
with open(r'C:\Users\HP\OneDrive\Documents\opencode_work\arcgis_exports\HB_Parcels.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    print(f'Columns ({len(headers)}):')
    for i, h in enumerate(headers):
        print(f'  {i}: {h}')
    row = next(reader)
    print(f'\nFirst row sample:')
    for h, v in zip(headers[:15], row[:15]):
        val = v[:50] if v else 'EMPTY'
        print(f'  {h}: {val}')
