"""Build Out-of-State LLC Timing Matrix: Property → PPP delta analysis"""
import os, pandas as pd
os.environ["GOOGLE_CLOUD_PROJECT"] = "noble-beanbag-497411-m4"
from google.cloud import bigquery
client = bigquery.Client()
PRJ = "noble-beanbag-497411-m4"

q = f"""
WITH llc_base AS (
    SELECT 
        Owner1 AS llc_name,
        Owner2,
        SiteAddress AS property_address,
        MailAddress AS mailing_address,
        MailCity AS mail_city,
        APN,
        LastSeller,
        LastSaleDate,
        SAFE_CAST(LastSaleValue AS FLOAT64) AS sale_price,
        UPPER(REGEXP_REPLACE(Owner1, r'[-.,&/() ]', '')) AS clean_name
    FROM `{PRJ}.ppp_rico.hb_llcs`
    WHERE Owner1 IS NOT NULL AND Owner1 != ''
),
ppp_matched AS (
    SELECT 
        BorrowerName,
        BorrowerCity AS ppp_city,
        BorrowerState AS ppp_state,
        CAST(CurrentApprovalAmount AS FLOAT64) AS ppp_amount,
        CAST(ForgivenessAmount AS FLOAT64) AS ppp_forgiven,
        DateApproved AS ppp_date,
        LoanStatus AS ppp_status,
        BusinessType,
        NAICSCode,
        NonProfit,
        JobsReported,
        ServicingLenderName AS ppp_lender,
        OriginatingLender,
        OriginatingLenderCity AS lender_city,
        OriginatingLenderState AS lender_state,
        UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
    FROM `{PRJ}.ppp_rico.ppp_150k_plus`
    UNION ALL
    SELECT 
        BorrowerName,
        BorrowerCity,
        BorrowerState,
        CAST(CurrentApprovalAmount AS FLOAT64),
        CAST(ForgivenessAmount AS FLOAT64),
        DateApproved,
        LoanStatus,
        BusinessType,
        NAICSCode,
        NonProfit,
        JobsReported,
        ServicingLenderName,
        OriginatingLender,
        OriginatingLenderCity,
        OriginatingLenderState,
        UPPER(REGEXP_REPLACE(BorrowerName, r'[-.,&/() ]', '')) AS clean_name
    FROM `{PRJ}.ppp_rico.ppp_up_to_150k`
),
joined AS (
    SELECT 
        l.llc_name,
        l.property_address,
        l.mailing_address,
        l.mail_city,
        l.APN,
        l.LastSeller,
        l.LastSaleDate,
        l.sale_price,
        p.BorrowerName AS ppp_borrower,
        p.ppp_city,
        p.ppp_state,
        p.ppp_amount,
        p.ppp_forgiven,
        p.ppp_date,
        p.ppp_status,
        p.BusinessType,
        p.NAICSCode,
        p.NonProfit,
        p.JobsReported,
        p.ppp_lender,
        p.OriginatingLender AS orig_lender,
        p.lender_city,
        p.lender_state,
        -- Calculate timing delta
        DATE_DIFF(
            SAFE.PARSE_DATE('%m/%d/%Y', p.ppp_date),
            SAFE.PARSE_DATE('%m/%d/%Y', l.LastSaleDate),
            DAY
        ) AS days_property_to_ppp,
        -- Out-of-state flag
        CASE 
            WHEN UPPER(p.ppp_state) != 'CA' AND UPPER(p.ppp_state) IS NOT NULL 
            THEN TRUE ELSE FALSE 
        END AS is_out_of_state_ppp,
        CASE
            WHEN UPPER(l.mail_city) NOT IN ('HUNTINGTON BEACH','NEWPORT BEACH','COSTA MESA',
                'SEAL BEACH','FOUNTAIN VALLEY','WESTMINSTER','SANTA ANA','IRVINE','LONG BEACH')
            THEN TRUE ELSE FALSE
        END AS is_out_of_state_mail
    FROM llc_base l
    JOIN ppp_matched p ON l.clean_name = p.clean_name
)
SELECT *
FROM joined
WHERE ppp_amount > 0
ORDER BY ppp_amount DESC
"""

print("Querying timing matrix...")
df = client.query(q).to_dataframe()
print(f"Total matched rows: {len(df)}")

# Save
out = r"C:\Users\HP\OneDrive\Documents\opencode_work\out_of_state_timing_matrix.csv"
df.to_csv(out, index=False)

# Also save to osint-agent scratch
out2 = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\out_of_state_timing_matrix.csv"
df.to_csv(out2, index=False)

# Summary stats
print(f"\n=== TIMING MATRIX SUMMARY ===")
print(f"Total LLCs matched: {df['llc_name'].nunique()}")
print(f"Total PPP loan rows: {len(df)}")
print(f"Out-of-state PPP: {df['is_out_of_state_ppp'].sum()} rows")
print(f"Out-of-state mail: {df['is_out_of_state_mail'].sum()} rows")
print(f"Dual out-of-state (PPP + mail): {((df['is_out_of_state_ppp']) & (df['is_out_of_state_mail'])).sum()} rows")

# Top by PPP amount with timing
print(f"\n=== TOP 20 OUT-OF-STATE BY PPP AMOUNT ===")
top = df.nlargest(20, 'ppp_amount')
for _, r in top.iterrows():
    delta = r['days_property_to_ppp']
    delta_str = f"{delta:+d}d" if pd.notna(delta) else "N/A"
    oos = "OUT" if r['is_out_of_state_ppp'] else "IN "
    print(f"  ${r['ppp_amount']:>10,.0f}  [{oos}] {delta_str:>8s}  {r['llc_name'][:30]:30s}  {r['ppp_city']}, {r['ppp_state']}  →  {r['mail_city']}")

# Timing distribution for out-of-state LLCs
oos = df[df['is_out_of_state_ppp'] == True]
if len(oos) > 0:
    print(f"\n=== OUT-OF-STATE TIMING DISTRIBUTION ===")
    print(f"Count: {len(oos)}")
    print(f"Mean delta: {oos['days_property_to_ppp'].mean():.0f} days")
    print(f"Min delta: {oos['days_property_to_ppp'].min():.0f} days")
    print(f"Max delta: {oos['days_property_to_ppp'].max():.0f} days")
    
    # Clusters
    print(f"\nTiming clusters:")
    for label, lo, hi in [("0-365 days (same year)", 0, 365), ("366-730 days (1-2yr)", 366, 730), ("730+ days (2yr+)", 731, 99999)]:
        cnt = ((oos['days_property_to_ppp'] >= lo) & (oos['days_property_to_ppp'] <= hi)).sum()
        print(f"  {label}: {cnt}")

# Top lenders for out-of-state
print(f"\n=== TOP LENDERS (OUT-OF-STATE PPP) ===")
lender_counts = oos.groupby('ppp_lender').agg(
    loans=('ppp_amount', 'count'),
    total=('ppp_amount', 'sum')
).sort_values('total', ascending=False).head(10)
for lender, row in lender_counts.iterrows():
    print(f"  {row['loans']:3d} loans  ${row['total']:>10,.0f}  {lender[:60]}")

print(f"\nSaved: {out}")
print(f"Saved: {out2}")
