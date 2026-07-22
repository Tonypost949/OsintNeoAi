from google.cloud import bigquery
import json

client = bigquery.Client()

PROJECT = "noble-beanbag-497411-m4"
DATASET = "ppp_rico"
TABLE = "oc_procurement"

print("==================================================")
print("AUDITING NEWLY INGESTED OC PROCUREMENT DATA")
print("==================================================\n")

# Query 1: How many rows have extracted vendors?
q1 = f"""
SELECT COUNT(*) as cnt, COUNT(vendor_name) as with_vendor, COUNT(amount_est) as with_amount
FROM `{PROJECT}.{DATASET}.{TABLE}`
"""
print("Querying row stats...")
res1 = list(client.query(q1).result())[0]
print(f"Total Rows: {res1.cnt}")
print(f"Rows with extracted Vendor Name: {res1.with_vendor}")
print(f"Rows with extracted Estimated Amount: {res1.with_amount}\n")

# Query 2: Let's list some extracted vendors
q2 = f"""
SELECT title, department, vendor_name, amount_est 
FROM `{PROJECT}.{DATASET}.{TABLE}` 
WHERE vendor_name IS NOT NULL 
LIMIT 15
"""
print("Sample extracted vendors:")
rows2 = client.query(q2).result()
for r in rows2:
    print(f"  Vendor: {r.vendor_name} | Amt: {r.amount_est} | Title: {r.title}")

# Query 3: Cross-reference OC Procurement vendors against ppp_150k_plus (national PPP) or hb_llcs
print("\nCross-referencing OC Procurement vendors against PPP & LLC databases...")
q3 = f"""
SELECT DISTINCT p.vendor_name, p.title, p.department, p.amount_est,
       ppp.BorrowerName, ppp.BorrowerCity, ppp.BorrowerState, ppp.InitialApprovalAmount
FROM `{PROJECT}.{DATASET}.{TABLE}` p
JOIN `{PROJECT}.{DATASET}.ppp_150k_plus` ppp
  ON UPPER(p.vendor_name) = UPPER(ppp.BorrowerName)
  OR UPPER(p.vendor_name) LIKE CONCAT('%', UPPER(ppp.BorrowerName), '%')
  OR UPPER(ppp.BorrowerName) LIKE CONCAT('%', UPPER(p.vendor_name), '%')
WHERE p.vendor_name IS NOT NULL
  AND LENGTH(p.vendor_name) > 4
  AND ppp.BorrowerName IS NOT NULL
  AND LENGTH(ppp.BorrowerName) > 4
LIMIT 30
"""
rows3 = list(client.query(q3).result())
print(f" -> Found {len(rows3)} matches with PPP borrowers!")
for idx, r in enumerate(rows3[:15]):
    print(f"  [{idx+1}] OC Vendor: {r.vendor_name} | PPP Borrower: {r.BorrowerName} ({r.BorrowerCity}, {r.BorrowerState}) | PPP Amt: ${float(r.InitialApprovalAmount):,.2f}")

# Query 4: Match against hb_llcs
print("\nCross-referencing OC Procurement vendors against Huntington Beach/OC property LLCs...")
q4 = f"""
SELECT DISTINCT p.vendor_name, p.title, llc.Owner1, llc.SiteAddress, llc.MailCity, llc.LastSaleValue
FROM `{PROJECT}.{DATASET}.{TABLE}` p
JOIN `{PROJECT}.{DATASET}.hb_llcs` llc
  ON UPPER(p.vendor_name) = UPPER(llc.Owner1)
  OR UPPER(p.vendor_name) LIKE CONCAT('%', UPPER(llc.Owner1), '%')
  OR UPPER(llc.Owner1) LIKE CONCAT('%', UPPER(p.vendor_name), '%')
WHERE p.vendor_name IS NOT NULL
  AND LENGTH(p.vendor_name) > 4
LIMIT 30
"""
rows4 = list(client.query(q4).result())
print(f" -> Found {len(rows4)} matches with LLC property owners!")
for idx, r in enumerate(rows4[:15]):
    print(f"  [{idx+1}] OC Vendor: {r.vendor_name} | LLC Owner: {r.Owner1} | Address: {r.SiteAddress} ({r.MailCity}) | Sale: ${float(r.LastSaleValue or 0):,.2f}")
