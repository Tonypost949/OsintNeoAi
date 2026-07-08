"""Display timing matrix results (no unicode, no quote clashes)"""
import pandas as pd

df = pd.read_csv(r"C:\Users\HP\OneDrive\Documents\opencode_work\out_of_state_timing_matrix.csv")
print(f"Rows: {len(df)}, Unique LLCs: {df['llc_name'].nunique()}")
print(f"Out-of-state PPP rows: {df['is_out_of_state_ppp'].sum()}")

print()
top = df.nlargest(25, 'ppp_amount')
header = f"{'LLC':35s} {'PPP':>10s} {'Delta':>7s} {'PPP City':20s} {'St':4s} {'Mail City':16s} {'NAICS':6s}"
print(header)
print("-" * 105)
for _, r in top.iterrows():
    delta = r['days_property_to_ppp']
    delta_str = f"{int(delta):+d}d" if pd.notna(delta) else "N/A"
    oos = "*" if r['is_out_of_state_ppp'] else " "
    llc = str(r['llc_name'])[:33]
    city = str(r['ppp_city'])[:18]
    st = str(r['ppp_state'])[:4]
    mc = str(r['mail_city'])[:16]
    naics = str(r['NAICSCode'])[:6]
    print(f"[{oos}] {llc:33s} ${r['ppp_amount']:>9,.0f} {delta_str:>7s} {city:18s} {st:4s} {mc:16s} {naics:6s}")

print()
print("TIMING CLUSTERS (out-of-state PPP):")
oos = df[df['is_out_of_state_ppp'] == True]
for label, lo, hi in [("0-365d (same year)", 0, 365), ("366-730d (1-2yr)", 366, 730), ("730+d (2yr+)", 731, 99999)]:
    cnt = ((oos['days_property_to_ppp'] >= lo) & (oos['days_property_to_ppp'] <= hi)).sum()
    print(f"  {label}: {cnt}")

print()
print("TOP LENDERS (out-of-state):")
lc = oos.groupby('ppp_lender').agg(n=('ppp_amount','count'), total=('ppp_amount','sum')).sort_values('total',ascending=False).head(8)
for lender, row in lc.iterrows():
    print(f"  {int(row['n']):3d} loans  ${row['total']:>10,.0f}  {str(lender)[:60]}")

print()
print("TOP ORIG LENDER CITIES (out-of-state):")
oc = oos.groupby('lender_city').agg(n=('ppp_amount','count'), total=('ppp_amount','sum')).sort_values('total',ascending=False).head(8)
for city, row in oc.iterrows():
    print(f"  {int(row['n']):3d} loans  ${row['total']:>10,.0f}  {str(city)}")
