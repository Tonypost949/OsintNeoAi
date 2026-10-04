from google.cloud import bigquery
bq = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== MERCY HOUSE / NAVIGATION CENTER PROPERTY VALUES ===")
results = bq.query("""
SELECT entity_name, property_address, property_city, property_apn, property_acquisition_value, property_acquisition_date, last_seller, ppp_loan_count, ppp_total_amount, ppp_total_forgiven
FROM `noble-beanbag-497411-m4.forensic_layers.ppp_property_bridge`
WHERE entity_name LIKE '%Mercy%' OR entity_name LIKE '%Navigation%'
""").result()
for r in results:
    print(f"Entity: {r.entity_name}")
    print(f"  Address: {r.property_address}, {r.property_city}")
    print(f"  APN: {r.property_apn}")
    acq_val = r.property_acquisition_value
    if acq_val:
        print(f"  Acquisition Value: ${acq_val:,.0f}")
    print(f"  Acquisition Date: {r.property_acquisition_date}")
    print(f"  Last Seller: {r.last_seller}")
    print(f"  PPP Loans: {r.ppp_loan_count} | Total: ${r.ppp_total_amount:,.0f} | Forgiven: ${r.ppp_total_forgiven:,.0f}")
    print()

print("\n=== BEACH BLVD CLUSTER - ALL PROPERTIES ===")
results = bq.query("""
SELECT SiteAddress, Owner1, Owner2, LastSaleValue, LastSaleDate, LastSeller, APN, risk_tier
FROM `noble-beanbag-497411-m4.ppp_rico.beach_blvd_cluster`
WHERE SiteAddress LIKE '%Beach Blvd%' OR SiteAddress LIKE '%Cameron%'
ORDER BY LastSaleValue DESC
""").result()
for r in results:
    print(f"{r.SiteAddress}")
    print(f"  APN: {r.APN}")
    print(f"  Owner: {r.Owner1} | {r.Owner2}")
    lv = r.LastSaleValue
    if lv:
        print(f"  Last Sale: ${lv:,.0f} on {r.LastSaleDate} (Seller: {r.LastSeller})")
    print(f"  Risk Tier: {r.risk_tier}")
    print()

print("\n=== CHDO REAL ESTATE TRANSACTIONS (MERCY HOUSE) ===")
results = bq.query("""
SELECT chdo_llc, project_name, transaction_type, amount, flags
FROM `noble-beanbag-497411-m4.forensic_layers.chdo_real_estate_transactions`
WHERE chdo_llc LIKE '%Mercy%'
ORDER BY amount DESC
""").result()
for r in results:
    amt = r.amount
    if amt:
        print(f"{r.chdo_llc} | {r.project_name} | {r.transaction_type} | ${amt:,.0f} | {r.flags}")
    else:
        print(f"{r.chdo_llc} | {r.project_name} | {r.transaction_type} | [Amount not specified] | {r.flags}")

print("\n=== PPP RICO EVIDENCE MATRIX - PROPERTY VALUES ===")
results = bq.query("""
SELECT llc_name, property_address, last_sale_value, ppp_loan_count, ppp_total_amount, ppp_total_forgiven
FROM `noble-beanbag-497411-m4.ppp_rico.rico_evidence_matrix`
WHERE llc_name LIKE '%Mercy%' OR llc_name LIKE '%Navigation%' OR property_address LIKE '%17631%' OR property_address LIKE '%17642%' OR property_address LIKE '%Beach Blvd%'
ORDER BY last_sale_value DESC
""").result()
for r in results:
    print(f"{r.llc_name}")
    print(f"  Address: {r.property_address}")
    lsv = r.last_sale_value
    if lsv:
        print(f"  Last Sale Value: ${lsv:,.0f}")
    print(f"  PPP Loans: {r.ppp_loan_count} | Total: ${r.ppp_total_amount:,.0f} | Forgiven: ${r.ppp_total_forgiven:,.0f}")
    print()