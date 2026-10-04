from google.cloud import bigquery
bq = bigquery.Client(project='noble-beanbag-497411-m4')

print('=== HBNC TIMELINE (FCA) ===')
results = bq.query("""
SELECT event_date, snippet, signal_type, entity_referenced, docket_number, risk_level
FROM `noble-beanbag-497411-m4.forensic_layers.fca_timeline`
WHERE snippet LIKE '%HBNC%' OR snippet LIKE '%17631%' OR snippet LIKE '%17642%' OR snippet LIKE '%Cameron%'
ORDER BY event_date
""").result()
for r in results:
    print(f'{r.event_date}: [{r.signal_type}] {r.snippet[:300]}...')
    print()

print('\n=== MERCY HOUSE PPP/RICO (rico_evidence_matrix) ===')
results = bq.query("""
SELECT llc_name, property_address, ppp_loan_count, ppp_total_amount, ppp_total_forgiven, ppp_names_matched
FROM `noble-beanbag-497411-m4.ppp_rico.rico_evidence_matrix`
WHERE llc_name LIKE '%Mercy%' OR llc_name LIKE '%Navigation%'
""").result()
for r in results:
    print(f'{r.llc_name} | {r.property_address} | Loans: {r.ppp_loan_count} | Total: ${r.ppp_total_amount} | Forgiven: ${r.ppp_total_forgiven} | Names: {r.ppp_names_matched}')

print('\n=== BEACH BLVD CLUSTER ===')
results = bq.query("""
SELECT SiteAddress, Owner1, Owner2, LastSaleValue, risk_tier
FROM `noble-beanbag-497411-m4.ppp_rico.beach_blvd_cluster`
WHERE SiteAddress LIKE '%Beach Blvd%' OR SiteAddress LIKE '%Cameron%'
ORDER BY LastSaleValue DESC
LIMIT 20
""").result()
for r in results:
    print(f'{r.SiteAddress} | {r.Owner1} | {r.Owner2} | ${r.LastSaleValue} | {r.risk_tier}')

print('\n=== GEOTRACKER USTs NEAR HBNC ===')
results = bq.query("""
SELECT business_name, address, city, latitude, longitude
FROM `noble-beanbag-497411-m4.forensic_layers.geotracker_ust`
WHERE latitude BETWEEN 33.69 AND 33.72
  AND longitude BETWEEN -117.99 AND -117.97
  AND (business_name LIKE '%G&M%' OR business_name LIKE '%76%' OR business_name LIKE '%Shell%' OR business_name LIKE '%Oil%')
ORDER BY business_name
""").result()
for r in results:
    print(f'{r.business_name} | {r.address}, {r.city} | {r.latitude}, {r.longitude}')

print('\n=== OC PROCUREMENT - HBNC RELATED ===')
results = bq.query("""
SELECT title, department, status, deadline, amount_est, vendor_name
FROM `noble-beanbag-497411-m4.ppp_rico.oc_procurement`
WHERE title LIKE '%Barrett%' OR title LIKE '%Navigation%' OR title LIKE '%shelter%' OR title LIKE '%Cameron%'
ORDER BY deadline DESC
""").result()
for r in results:
    print(f'{r.title} | {r.department} | {r.status} | {r.deadline} | {r.amount_est} | {r.vendor_name}')

print('\n=== CHDO REAL ESTATE (MERCY HOUSE) ===')
results = bq.query("""
SELECT chdo_llc, project_name, transaction_type, amount, flags
FROM `noble-beanbag-497411-m4.forensic_layers.chdo_real_estate_transactions`
WHERE chdo_llc LIKE '%Mercy%'
""").result()
for r in results:
    print(f'{r.chdo_llc} | {r.project_name} | {r.transaction_type} | ${r.amount} | {r.flags}')

print('\n=== NATIONAL AUDITS - DRIVE FILES HBNC ===')
results = bq.query("""
SELECT file_name, mime_type, modified_time, size_bytes
FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
WHERE file_name LIKE '%HBNC%' OR file_name LIKE '%Cameron%' OR file_name LIKE '%17642%' OR file_name LIKE '%17631%'
ORDER BY modified_time DESC
LIMIT 30
""").result()
for r in results:
    print(f'{r.file_name[:100]} | {r.mime_type} | {r.modified_time} | {r.size_bytes} bytes')