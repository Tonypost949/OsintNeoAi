-- Update the CA row in project-743aab84-f9a5-4ec7-954 with real Huntington Beach Navigation Center details
UPDATE `project-743aab84-f9a5-4ec7-954.national_audits.all_state_records`
SET non_profiteers_index = ARRAY_CONCAT(IFNULL(non_profiteers_index, []), [
  STRUCT(
    "NPI-HBNC-MERCY" AS npi_id, 
    "Mercy House (Huntington Beach Navigation Center)" AS organization_name, 
    "OPERATING-AGREEMENT: $56.68/bed/night (164-174 beds)" AS cms_billing_code, 
    1100000.00 AS unaccounted_fund_delta
  )
])
WHERE state_code = 'CA';
