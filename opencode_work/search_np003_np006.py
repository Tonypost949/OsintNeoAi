import pandas as pd
import os

df = pd.read_csv(r'C:\Users\HP\OneDrive\Documents\opencode_work\rico_evidence_matrix.csv')

print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")

terms = ['united', 'community housing', '211', 'orange county', 'OC United', 'families forward']

for term in terms:
    mask = df.apply(lambda row: row.astype(str).str.contains(term, case=False, na=False).any(), axis=1)
    matches = df[mask]
    if len(matches) > 0:
        print(f"\n=== {term} ({len(matches)} matches) ===")
        for _, row in matches.head(5).iterrows():
            print(f"  LLC: {row['llc_name']} | Nonprofit: {row['nonprofit_name']} | EIN: {row['nonprofit_ein']} | City: {row['mail_city']}, {row['mail_state']}")
    else:
        print(f"\n=== {term} — NO MATCHES ===")

# Also check for any nonprofits near Santa Ana
print("\n\n=== Nonprofits in Santa Ana ===")
sa = df[df['mail_city'].astype(str).str.contains('Santa Ana', case=False, na=False)]
print(f"Count: {len(sa)}")
for _, row in sa.head(10).iterrows():
    print(f"  LLC: {row['llc_name']} | Nonprofit: {row['nonprofit_name']} | EIN: {row['nonprofit_ein']}")
