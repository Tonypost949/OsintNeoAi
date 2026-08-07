"""
Out-of-state connection analysis for:
  TRIUMVIRATE LLC
  STEWART INDUSTRIES LLC
  L2T MEDIA LLC

Goals:
  1. Find all LLCs in OC LLC data with same/related owners
  2. Cross-ref against PPP loans for those owners
  3. Cross-ref against national LLC data / OSINT entities
  4. Build full out-of-state connection map
"""
from google.cloud import bigquery
from pathlib import Path

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
client = bigquery.Client(project="noble-beanbag-497411-m4")

TARGET_ENTITIES = ["TRIUMVIRATE LLC", "STEWART INDUSTRIES LLC", "L2T MEDIA LLC"]

print("=" * 60)
print("1. OC LLC RECORDS FOR TARGET ENTITIES")
print("=" * 60)
for name in TARGET_ENTITIES:
    q = f"""
        SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity,
               APN, LastSeller, LastSaleDate, LastSaleValue
        FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
        WHERE UPPER(Owner1) LIKE '%{name.upper()}%'
           OR UPPER(Owner2) LIKE '%{name.upper()}%'
           OR UPPER(MailAddress) LIKE '%{name.upper()}%'
        LIMIT 10
    """
    df = client.query(q).to_dataframe()
    print(f"\n--- {name} ---")
    if df.empty:
        print("  No OC LLC records found")
    else:
        print(df.to_string())

print("\n" + "=" * 60)
print("2. PPP LOANS FOR TARGET ENTITIES (all states)")
print("=" * 60)
for name in TARGET_ENTITIES:
    q = f"""
        SELECT LoanNumber, BorrowerName, BorrowerAddress, BorrowerCity,
               BorrowerState, InitialApprovalAmount, LoanStatus, DateApproved,
               ServicingLenderName, NAICSCode
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
        WHERE UPPER(BorrowerName) LIKE '%{name.upper()}%'
           OR UPPER(BorrowerName) LIKE '%{name.replace(" ", "%").upper()}%'
        LIMIT 10
    """
    df = client.query(q).to_dataframe()
    print(f"\n--- {name} PPP ---")
    if df.empty:
        print("  No PPP records found")
    else:
        print(df.to_string())

print("\n" + "=" * 60)
print("3. OUT-OF-STATE LLC OWNER NETWORK (same owners as TRIUMVIRATE)")
print("=" * 60)

# Find owners of TRIUMVIRATE LLC
q_tri = """
    SELECT Owner1, Owner2, MailAddress, MailCity
    FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
    WHERE UPPER(Owner1) LIKE '%TRIUMVIRATE%'
       OR UPPER(Owner2) LIKE '%TRIUMVIRATE%'
    LIMIT 5
"""
tri_df = client.query(q_tri).to_dataframe()
tri_owners = set()
for _, row in tri_df.iterrows():
    if row['Owner1'] and str(row['Owner1']) != 'nan': tri_owners.add(str(row['Owner1']).strip())
    if row['Owner2'] and str(row['Owner2']) != 'nan': tri_owners.add(str(row['Owner2']).strip())

print(f"TRIUMVIRATE owners: {tri_owners}")

# Find all OC LLCs owned by same persons
if tri_owners:
    owner_list = " OR ".join([f"(Owner1 LIKE '%{o}%' OR Owner2 LIKE '%{o}%')" for o in tri_owners])
    q_net = f"""
        SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, MailState,
               LastSeller, LastSaleDate, LastSaleValue
        FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
        WHERE {owner_list}
           AND UPPER(Owner1) NOT LIKE '%TRIUMVIRATE%'
           AND UPPER(Owner2) NOT LIKE '%TRIUMVIRATE%'
        ORDER BY LastSaleValue DESC
        LIMIT 20
    """
    net_df = client.query(q_net).to_dataframe()
    print(f"\nOther OC LLCs by same owners ({len(net_df)} found):")
    print(net_df.to_string())

print("\n" + "=" * 60)
print("4. OUT-OF-STATE LLC OWNER NETWORK (STEWART INDUSTRIES)")
print("=" * 60)

q_stw = """
    SELECT Owner1, Owner2, MailAddress, MailCity
    FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
    WHERE UPPER(Owner1) LIKE '%STEWART%'
       OR UPPER(Owner2) LIKE '%STEWART%'
       OR UPPER(Owner1) LIKE '%STEWART INDUSTRIES%'
    LIMIT 5
"""
stw_df = client.query(q_stw).to_dataframe()
stw_owners = set()
for _, row in stw_df.iterrows():
    if row['Owner1'] and str(row['Owner1']) != 'nan': stw_owners.add(str(row['Owner1']).strip())
    if row['Owner2'] and str(row['Owner2']) != 'nan': stw_owners.add(str(row['Owner2']).strip())

print(f"STEWART INDUSTRIES owners: {stw_owners}")

if stw_owners:
    owner_list = " OR ".join([f"(Owner1 LIKE '%{o}%' OR Owner2 LIKE '%{o}%')" for o in stw_owners])
    q_net2 = f"""
        SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity, MailState,
               LastSeller, LastSaleDate, LastSaleValue
        FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
        WHERE {owner_list}
           AND UPPER(Owner1) NOT LIKE '%STEWART%'
           AND UPPER(Owner2) NOT LIKE '%STEWART%'
        ORDER BY LastSaleValue DESC
        LIMIT 20
    """
    net2_df = client.query(q_net2).to_dataframe()
    print(f"\nOther OC LLCs by same owners ({len(net2_df)} found):")
    print(net2_df.to_string())

print("\n" + "=" * 60)
print("5. L2T MEDIA LLC — FULL PROFILE")
print("=" * 60)

# L2T MEDIA — find in OSINT entities too
q_l2t = """
    SELECT 'OSINT' as source, name, address, city, state, ein, type
    FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
    WHERE UPPER(name) LIKE '%L2T%' OR UPPER(name) LIKE '%L 2 T%'
    UNION ALL
    SELECT 'PPP' as source, BorrowerName, BorrowerAddress, BorrowerCity,
           BorrowerState, 'NA' as ein, LoanStatus as type
    FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
    WHERE UPPER(BorrowerName) LIKE '%L2T%'
    LIMIT 20
"""
l2t_df = client.query(q_l2t).to_dataframe()
print(l2t_df.to_string())

print("\n" + "=" * 60)
print("6. SEARCH ALL DATASETS FOR STEWART / TRIUMVIRATE / L2T IN OSINT")
print("=" * 60)

for term in ["STEWART", "TRIUMVIRATE", "L2T MEDIA"]:
    q = f"""
        SELECT 'hb_church_osint.entities' as table, name, address, city, state, ein
        FROM `noble-beanbag-497411-m4.hb_church_osint.entities`
        WHERE UPPER(name) LIKE '%{term}%'
        LIMIT 5
    """
    try:
        df = client.query(q).to_dataframe()
        print(f"\n--- {term} in OSINT ---")
        print(df.to_string() if not df.empty else "  Not found")
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "=" * 60)
print("7. GRAMERCY / STEWART CONNECTION — SHARED ADDRESSES")
print("=" * 60)

# Find any LLCs with same mailing address as STEWART or TRIUMVIRATE
q_shared = """
    WITH tri_addresses AS (
        SELECT DISTINCT MailAddress, MailCity
        FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
        WHERE UPPER(Owner1) LIKE '%TRIUMVIRATE%'
           OR UPPER(Owner2) LIKE '%TRIUMVIRATE%'
    ),
    stw_addresses AS (
        SELECT DISTINCT MailAddress, MailCity
        FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs`
        WHERE UPPER(Owner1) LIKE '%STEWART%'
           OR UPPER(Owner2) LIKE '%STEWART%'
    )
    SELECT 'TRIUMVIRATE' as entity, h.Owner1, h.Owner2, h.SiteAddress, h.MailAddress, h.MailCity, h.LastSaleValue
    FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs` h
    WHERE h.MailAddress IN (SELECT MailAddress FROM tri_addresses)
       AND UPPER(h.Owner1) NOT LIKE '%TRIUMVIRATE%'
    UNION ALL
    SELECT 'STEWART' as entity, h.Owner1, h.Owner2, h.SiteAddress, h.MailAddress, h.MailCity, h.LastSaleValue
    FROM `noble-beanbag-497411-m4.ppp_rico.hb_llcs` h
    WHERE h.MailAddress IN (SELECT MailAddress FROM stw_addresses)
       AND UPPER(h.Owner1) NOT LIKE '%STEWART%'
    ORDER BY LastSaleValue DESC
    LIMIT 20
"""
shared_df = client.query(q_shared).to_dataframe()
print(shared_df.to_string())

print("\nDone.")
