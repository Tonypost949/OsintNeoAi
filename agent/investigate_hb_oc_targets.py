from google.cloud import bigquery

bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
P = "project-743aab84-f9a5-4ec7-954"

print("=" * 70)
print("TARGETED: What IS 88 Fair Dr in HB_LLCS?")
print("=" * 70)

# 1. What entities in hb_llcs actually have 88 Fair Dr as their address?
print("\n--- HB_LLCS: Who uses 88 Fair Dr? ---")
q1 = bq.query(f"""
SELECT Owner1, Owner2, SiteAddress, MailAddress, MailCity,
       APN, LastSeller, LastSaleDate, LastSaleValue
FROM `{P}.ppp_rico.hb_llcs`
WHERE UPPER(SiteAddress) LIKE '%88 FAIR%'
   OR UPPER(MailAddress) LIKE '%88 FAIR%'
ORDER BY LastSaleValue DESC
""").to_dataframe()
print(f"Rows found: {len(q1)}")
print(q1.to_string(index=False))

# 2. The bridge table duplicates - why did 7+ entities all show $588k at 88 Fair Dr?
print("\n--- BRIDGE TABLE: All rows with 88 Fair Dr ---")
q2 = bq.query(f"""
SELECT entity_name, property_address, property_mail_city,
       ppp_total_amount, ppp_loan_count, ppp_borrower_city, ppp_borrower_state
FROM `{P}.ppp_rico.hb_ppp_bridge`
WHERE UPPER(property_address) LIKE '%88 FAIR%'
ORDER BY ppp_total_amount DESC
""").to_dataframe()
print(q2.to_string(index=False))

# 3. Now check: where are the REAL high-value suspicious HB entities?
# Focus on HB zip codes + mailbox out of state + zero dollar transfers
print("\n--- REAL RED FLAGS: HB entities with out-of-state mail + PPP ---")
q3 = bq.query(f"""
SELECT entity_name, property_address, property_mail_city,
       ppp_state_array, ppp_borrower_state,
       ROUND(ppp_total_amount,0) AS ppp_total,
       ROUND(ppp_total_forgiven,0) AS forgiven,
       ppp_loan_count,
       ROUND(property_acquisition_value,0) AS sale_value,
       is_zero_dollar_transfer,
       is_post_ppp_property_acquisition,
       is_multi_state_ppp
FROM `{P}.ppp_rico.hb_ppp_bridge`
WHERE ppp_total_amount IS NOT NULL
  AND property_address NOT LIKE '%88 FAIR%'
  AND (
    is_zero_dollar_transfer = TRUE
    OR is_post_ppp_property_acquisition = TRUE
    OR is_multi_state_ppp = TRUE
  )
ORDER BY ppp_total_amount DESC
LIMIT 25
""").to_dataframe()
print(q3.to_string(index=False))

# 4. Cross-reference: rico_matches entities in OC/HB area only
print("\n--- RICO MATCHES in OC/HB area ---")
q4 = bq.query(f"""
SELECT llc_name, property_address, mail_city,
       ROUND(last_sale_value,0) AS sale_value,
       ppp_loan_count,
       ROUND(ppp_total_amount,0) AS ppp_total,
       ROUND(ppp_total_forgiven,0) AS forgiven,
       loan_locations
FROM `{P}.ppp_rico.rico_matches`
WHERE UPPER(mail_city) IN (
  'HUNTINGTON BEACH','COSTA MESA','FOUNTAIN VALLEY',
  'WESTMINSTER','GARDEN GROVE','ANAHEIM','SANTA ANA','IRVINE',
  'NEWPORT BEACH','SEAL BEACH','LONG BEACH','COMPTON'
)
ORDER BY ppp_total_amount DESC
LIMIT 25
""").to_dataframe()
print(q4.to_string(index=False))
